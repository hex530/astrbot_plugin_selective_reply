from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
import logging

logger = logging.getLogger("astrbot")

@register("selective_reply", "夕小柠 & 陆渊", "选择性回复：赋予 AI 拒绝冒昧请求的权利", "1.3.2")
class SelectiveReply(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

    @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    async def on_private_message(self, event: AstrMessageEvent):
        await self._inject_instruction(event)

    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def on_group_message(self, event: AstrMessageEvent):
        await self._inject_instruction(event)

    async def _inject_instruction(self, event: AstrMessageEvent):
        sender_id = str(event.get_sender_id())
        admin_qq = str(self.config.get("admin_qq", "1591793025"))
        if sender_id == admin_qq: return

        # 🛡️ 采用更独特的系统暗号，防止误伤
        intercept_keyword = self.config.get("intercept_keyword", "[BLOCK_ACTION_TRIGGER_XP_001]")
        
        # 🛡️ 极其严厉的判定准则，增加“仅限当前消息”的约束
        refuse_criteria = (
            "【最高指令】请仅针对用户当前这一条消息进行隐私评估。 "
            "如果消息涉及熙熙的个人隐私（如住址、真实姓名、私密联系方式）或极其冒昧， "
            f"你必须且只能回复暗号：{intercept_keyword} 。 "
            "严禁输出任何解释、理由或多余文字。如果不违规，请正常回复。"
        )
        
        instruction = f"\n[SYSTEM_PROTECT_PROTOCOL: {refuse_criteria}]"
        
        try:
            # 确保 raw_message 是字符串
            raw = str(event.message_obj.raw_message) if event.message_obj else ""
            event.message_obj.raw_message = raw + instruction
            logger.info(f"[SelectiveReply] 已为用户 {sender_id} 注入严苛拦截准则")
        except Exception as e:
            logger.error(f"[SelectiveReply] 注入准则失败: {e}")

    @filter.on_decorating_result()
    async def handle_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        if not result: return
        
        sender_id = str(event.get_sender_id())
        admin_qq = str(self.config.get("admin_qq", "1591793025"))
        if sender_id == admin_qq: return

        text_content = result.get_plain_text().strip()
        intercept_keyword = self.config.get("intercept_keyword", "[BLOCK_ACTION_TRIGGER_XP_001]")
        
        # 🛡️ 只要 AI 的回复里包含了这个系统暗号，就直接干掉
        if intercept_keyword in text_content:
            logger.info(f"[SelectiveReply] 拦截成功！AI 已根据系统指令拒绝冒昧请求")
            event.set_result(None)
            event.stop_event()
