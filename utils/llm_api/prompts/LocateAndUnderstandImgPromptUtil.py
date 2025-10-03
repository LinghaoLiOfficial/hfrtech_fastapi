class LocateAndUnderstandImgPromptUtil:
    @classmethod
    def generate(cls, image_path):
        system_prompt = """
             请识别整个图片的长宽大小，用户输入图片中的实体对象给出对应所在图片的位置坐标和描述，以及输入图片中的文字对象给出对应所在图片的位置坐标和描述，输出为json格式。示例预期输出: 
             {
                 "image_size": {
                     "width": 840,
                     "height": 1120
                 },
                 "overall_description": {
                     "content_description": "图片展示了一个室内场景，主要元素包括一张铺有白色被子的床、床头挂着的布帘、床上放置的超市传单、一个猫脸表情包以及相关的文字说明。整体传达了一种在日常生活中通过想象购物来获得小确幸的感觉。",
                     "style_description": "图片风格偏向生活化和幽默感，通过简单的家居场景和有趣的表情包结合文字，营造出一种轻松愉快的氛围。"
                 },
                 "entities": [
                     {
                         "label": "床和床上的被子",
                         "bbox_2d": [
                             0,
                             0,
                             840,
                             920
                         ],
                         "content_description": "一张铺有白色被子的床，被子整齐地放在床上，营造出一种温馨的休息环境。",
                         "style_description": "简洁实用，具有居家生活的典型特征。"
                     },
                     {
                         "label": "超市传单",
                         "bbox_2d": [
                             210,
                             550,
                             430,
                             750
                         ],
                         "content_description": "一张色彩鲜艳的超市促销传单，上面印有各种商品的图片和价格信息，吸引人注意。",
                         "style_description": "色彩丰富，设计吸引眼球，典型的商业宣传风格。"
                     },
                     {
                         "label": "猫的表情包",
                         "bbox_2d": [
                             405,
                             535,
                             620,
                             765
                         ],
                         "content_description": "一个猫脸表情包，表情显得有些困惑或思考状，代表图片中的我在思考或幻想。",
                         "style_description": "可爱有趣，带有幽默感，常用于网络表达情感。"
                     },
                     {
                         "label": "床头布帘",
                         "bbox_2d": [
                             0,
                             0,
                             840,
                             380
                         ],
                         "content_description": "挂在床头的白色布帘，增加了房间的私密性和装饰性，使空间看起来更加舒适。",
                         "style_description": "简约大方，符合居家装饰的常见风格。"
                     },
                     {
                         "label": "木质床架",
                         "bbox_2d": [
                             0,
                             770,
                             840,
                             920
                         ],
                         "content_description": "床的底部是木质床架，坚固且具有自然的质感，与整体家居风格相协调。",
                         "style_description": "自然朴实，体现木质家具的经典美感。"
                     },
                     {
                         "label": "桌子一角",
                         "bbox_2d": [
                             0,
                             790,
                             200,
                             1120
                         ],
                         "content_description": "图片左下角可见的一部分木质桌子，桌子上似乎放置了一些物品，增加了场景的生活气息。",
                         "style_description": "实用性强，体现了日常生活的真实场景。"
                     }
                 ],
                 "texts": [
                     {
                         "text_content": "平淡日子里的幸福",
                         "bbox_2d": [
                             130,
                             58,
                             700,
                             120
                         ],
                         "content_description": "位于图片顶部的文字，表达了在平凡的日常生活中也能找到小确幸的主题。",
                         "style_description": "黑色字体，字体较大，简洁明了，作为图片的主题突出显示。"
                     },
                     {
                         "text_content": "我",
                         "bbox_2d": [
                             625,
                             670,
                             695,
                             740
                         ],
                         "content_description": "位于猫表情包旁边的文字，表示这个表情包代表的是“我”，即图片的主人公。",
                         "style_description": "黄色字体，字体大小适中，醒目且具有强调效果，直接指代表情包。"
                     },
                     {
                         "text_content": "幻想着买什么",
                         "bbox_2d": [
                             280,
                             775,
                             640,
                             835
                         ],
                         "content_description": "位于图片下方的文字，表达了主人公在看到超市传单时，开始想象自己要购买的商品。",
                         "style_description": "白色字体，字体大小适中，补充说明主人公的心理活动。"
                     }
                 ]
             }
            """

        user_prompt = "请识别整个图片的长宽大小，用户输入图片中的实体对象给出对应所在图片的位置坐标和描述，以及输入图片中的文字对象给出对应所在图片的位置坐标和描述，输出为json格式"

        template = [
            {
                "role": "system",
                "content": [{"text": system_prompt}]
            },
            {
                "role": "user",
                "content": [
                    {'image': image_path},
                    {'text': user_prompt}
                ]
            }
        ]

        return template
