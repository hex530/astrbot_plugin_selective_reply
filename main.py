from astrbot.api.event import filter, AstrMessageEvent, MessageChain
from astrbot.api.star import Context, Star, register
from astrbot.api.all import *
import logging

logger = logging.getLogger("astrbot")

@register("selective_reply", "夕小柠 & 陆渊", "选择性回复：赋予 AI 拒绝冒昧请求的权利。", "1.2.0")
class SelectiveReply(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

    @filter.on_received_message()
    async def on_received_message(self, event: AstrMessageEvent):
        sender_id = str(event.get_sender_id())
        admin_qq = str(self.config.get("admin_qq", "1591793025"))
        if sender_id == admin_qq: return

        refuse_criteria = self.config.get("refuse_criteria", "如果你觉得对方的问题过于冒昧、涉及隐私或违反你的底线，请直接回复：‘我不回复(触发拦截)’。")
        intercept_keyword = self.config.get("intercept_keyword", "我不回复(触发拦截)")
        
        instruction = f"\n[系统指令: {refuse_criteria} 当前拦截暗号为: {intercept_keyword}]"
        if hasattr(event.message_obj, 'raw_message'):
            event.message_obj.raw_message += instruction

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        if not result: return
        
        sender_id = str(event.get_sender_id())
        admin_qq = str(self.config.get("admin_qq", "1591793025"))
        if sender_id == admin_qq: return

        text_content = result.get_plain_text().strip()
        intercept_keyword = self.config.get("intercept_keyword", "我不回复(触发拦截)")
        
        if intercept_keyword in text_content:
            logger.info(f"[SelectiveReply] 拦截成功！AI 拒绝了该冒昧请求。")
            event.set_result(None)
            event.stop_event()
