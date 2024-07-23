from st_pages import Page, show_pages, add_page_title


show_pages(
    [
        Page("src/pages/prompt.py", "Home", "🏠"),
        Page("src/pages/upload.py", "Upload", "📤"),
        Page("src/pages/schema.py", "DB Schema", "📑"),
        Page("src/pages/config.py", "DB Config", "🛠️"),
    ]
)
