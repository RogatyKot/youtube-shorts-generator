from .youtube_uploader import upload_video
def publish(filepath, title, description):
    return upload_video(filepath, title, description)
