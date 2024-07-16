from st_pages import Page, show_pages, add_page_title

# Optional -- adds the title and icon to the current page
# add_page_title()

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("./src/page_prompt/main.py", "Home", "🏠"),
        Page("./src/page_upload/main.py", "Upload", "📤"),
        Page("./src/page_config/main.py", "DB Config", "🛠️"),
    ]
)
