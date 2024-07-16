from st_pages import Page, show_pages, add_page_title

# Optional -- adds the title and icon to the current page
# add_page_title()

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("src/pages/prompt.py", "Home", "🏠"),
        Page("src/pages/upload.py", "Upload", "📤"),
        Page("src/pages/config.py", "DB Config", "🛠️"),
    ]
)
