class AnalysisVideoPromptUtil:
    @classmethod
    def generate(cls, video_url):
        template = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": [{
                "type": "video_url",
                "video_url": {
                    "url": video_url}},
                {"type": "text", "text": "请给出这段视频的详细剧本"}]
             }]

        return template

