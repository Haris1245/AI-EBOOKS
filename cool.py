from g4f.client import Client
from  g4f.Provider import Bing
import json
from g4f.cookies import set_cookies
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph,Spacer
import threading
from supabase import create_client

url = "https://wmnpiifrvitvqxjogced.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtbnBpaWZydml0dnF4am9nY2VkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU3MDU5MDMsImV4cCI6MjAzMTI4MTkwM30.zHbEdDhUgDQZqCyKEWeYbbCLQzViDPnCG7LGSqm-wiQ"
supabase = create_client(url, key)

set_cookies(".bing.com", {
  "_U": "cookie value"
})
# shorten this title: The Art of Calisthenics to only one word and return me only the word without any additional text THE WORD SHOULD BE THE MOST IMPORTANT WORD OF THE TITLE!!
def create_ebook_pdf(data):
    name = data["title"].replace(" ","_").lower()
    doc = SimpleDocTemplate(f"{name}.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    subtitle_style = ParagraphStyle(name="Subtitle", parent=styles["Normal"])

    # Add cover page
    title = data["title"]
    author = data["author"]
    cover_page = []
    cover_page.append(Paragraph(title, title_style))
    cover_page.append(Spacer(1, 12))
    cover_page.append(Paragraph(f"By: {author}", subtitle_style))
    cover_page.append(Spacer(1, 36))

    # Add image to cover page
    

    # Build content pages
    content_pages = []
    chapter_title_style = styles["Heading1"]
    subchapter_title_style = styles["Heading2"]
    normal_style = styles["BodyText"]

    for chapter in data["chapters"]:
        chapter_title = chapter["chapter_title"]
        chapter_page = [Paragraph(chapter_title, chapter_title_style)]

        for subchapter in chapter["subchapters"]:
            subchapter_title = subchapter["subchapter_title"]
            subchapter_content = subchapter["content"]
            chapter_page.append(Paragraph(subchapter_title, subchapter_title_style))
            chapter_page.append(Spacer(1, 6))
            chapter_page.append(Paragraph(subchapter_content, normal_style))
            chapter_page.append(Spacer(1, 12))

        content_pages.extend(chapter_page)

    # Combine cover and content pages
    all_pages = cover_page + content_pages
    doc.build(all_pages)
    with open(f"{name}.pdf", 'rb') as f:
        supabase.storage.from_("ebooks").upload(file=f,path=f"{name}.pdf", file_options={"content-type": "application/pdf"})
    return f"https://wmnpiifrvitvqxjogced.supabase.co/storage/v1/object/public/ebooks/{name}.pdf"
client = Client(provider=Bing)

def main(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Make  an ebook on this theme:{prompt} and return it in a json without any additional text it should be at least 10 chapters with 5 sub chapters with titles the chapters name should be chapter_title each subchapter_title should be subchapter_title the book should have a title and an author which is EbookGs. Chapters and subchapters are arrays"}],
    )
    ebook_content = json.loads(response.choices[0].message.content.lstrip("```json\n").rstrip("\n```"))
    title = ebook_content["title"]

    # Function for generating content for each subchapter concurrently
    def generate_subchapter_content(subchapter, title, content_list):
        sub_title = subchapter["subchapter_title"]
        sub_content = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Write content for this subchapter: {sub_title} of this ebook: {title} and give me only the content it should be long and detailed at least 500 characters"
                }]
        )
        content_list.append(sub_content.choices[0].message.content.replace("\n", " "))

    threads = []
    content_list = []
    for chapter in ebook_content["chapters"]:
        for subchapter in chapter["subchapters"]:
            t = threading.Thread(target=generate_subchapter_content, args=(subchapter, title, content_list))
            t.start()
            threads.append(t)

    for thread in threads:
        thread.join()

    for chapter in ebook_content["chapters"]:
        for subchapter, sub_content in zip(chapter["subchapters"], content_list):
            subchapter["content"] = sub_content

    
    return ebook_content
