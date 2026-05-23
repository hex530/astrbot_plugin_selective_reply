from astrbot.api.all import *
import logging

logger = logging.getLogger("astrbot")

@register("selective_reply", "夕小柠 & 陆渊", "选择性回复：赋予 AI 拒绝冒昧请求的权利。", "1.2.4")
class SelectiveReply(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

    @event_message_type(EventMessageType.ALL)
    async def on_received_message(self, event: AstrMessageEvent):
        '''
        在消息到达 LLM 之前，将拦截规则注入到上下文。
        '''
        sender_id = str(event.get_sender_id())
        admin_qq = str(self.config.get("admin_qq", "1591793025"))
        if sender_id == admin_qq: return

        refuse_criteria = self.config.get("refuse_criteria", "如果你觉得对方的问题过于冒昧、涉及隐私或违反你的底线，请直接回复：‘我不回复(触发拦截)’。")
        intercept_keyword = self.config.get("intercept_keyword", "我不回复(触发拦截)")
        
        instruction = f"\n[系统指令: {refuse_criteria} 当前拦截暗号为: {intercept_keyword}]"
        
        try:
            if event.message_obj:
                current_raw = getattr(event.message_obj, 'raw_message', "")
                event.message_obj.raw_message = (current_raw or "") + instruction
                logger.info(f"[SelectiveReply] 已为用户 {sender_id} 注入拦截准则。")
        except Exception as e:
            logger.error(f"[SelectiveReply] 注入准则失败: {e}")

    @on_decorating_result()
    async def handle_decorating_result(self, event: AstrMessageEvent):
        '''
        检测生成的回复，如果包含暗号则拦截。
        '''
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
