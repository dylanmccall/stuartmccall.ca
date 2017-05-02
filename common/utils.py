from markdown import markdown

def markdownify(content):
    return markdown(
        text=content,
        extensions=[],
        extension_configs=[]
    )
