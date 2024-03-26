"""Event handlers and hooks."""

import logging
from argparse import Namespace
from tempfile import NamedTemporaryFile
from typing import Any

from deltabot_cli import AttrDict, Bot, BotCli, ChatType, EventType, ViewType, events
from diffusers import StableDiffusionPipeline
from PIL import Image
from rich.logging import RichHandler

cli = BotCli("text2img-bot")
cli.add_generic_option(
    "--no-time",
    help="do not display date timestamp in log messages",
    action="store_false",
)
cli.add_generic_option(
    "--device",
    help="set the device type (default: %(default)s)",
    default="cpu",
    choices=[
        "cpu",
        "cuda",
        "ipu",
        "xpu",
        "mkldnn",
        "opengl",
        "opencl",
        "ideep",
        "hip",
        "ve",
        "fpga",
        "ort",
        "xla",
        "lazy",
        "vulkan",
        "mps",
        "meta",
        "hpu",
        "mtia",
        "privateuseone",
    ],
)
HELP = (
    "I'm a Delta Chat bot, send me a text message describing the image you want to generate."
    " It might take a while for your request to be processed, please, be patient.\n\n"
    "No 3rd party service is involved, only I will have access to the messages in this chat"
    " and I will delete all messages on my side after sending you the results."
)
pipe: Any = None


@cli.on_init
def on_init(bot: Bot, args: Namespace) -> None:
    level = logging.DEBUG if bot.logger.level == logging.DEBUG else logging.ERROR
    logging.basicConfig(level=level)
    bot.logger.handlers = [
        RichHandler(show_path=False, omit_repeated_times=False, show_time=args.no_time)
    ]
    for accid in bot.rpc.get_all_account_ids():
        if not bot.rpc.get_config(accid, "displayname"):
            bot.rpc.set_config(accid, "displayname", "Text To Image")
            status = "I'm a Delta Chat bot, send me a message describing the image you want to generate"
            bot.rpc.set_config(accid, "selfstatus", status)
            bot.rpc.set_config(accid, "delete_server_after", "1")
            bot.rpc.set_config(accid, "delete_device_after", str(60 * 60 * 24))


@cli.on_start
def on_start(_bot: Bot, args: Namespace) -> None:
    global pipe  # pylint: disable=W0603
    pipe = StableDiffusionPipeline.from_pretrained("prompthero/openjourney")
    pipe = pipe.to(args.device)


@cli.on(events.RawEvent)
def on_core_event(bot: Bot, accid: int, event: AttrDict) -> None:
    if event.kind == EventType.INFO:
        bot.logger.debug(event.msg)
    elif event.kind == EventType.WARNING:
        bot.logger.warning(event.msg)
    elif event.kind == EventType.ERROR:
        bot.logger.error(event.msg)
    elif event.kind == EventType.MSG_DELIVERED:
        bot.rpc.delete_messages(accid, [event.msg_id])
    elif event.kind == EventType.SECUREJOIN_INVITER_PROGRESS:
        if event.progress == 1000 and not bot.rpc.get_contact(event.contact_id).is_bot:
            bot.logger.debug("QR scanned by contact id=%s", event.contact_id)
            chatid = bot.rpc.create_chat_by_contact_id(accid, event.contact_id)
            bot.rpc.send_msg(accid, chatid, {"text": HELP})


@cli.on(events.NewMessage(is_bot=None))
def generate_img(bot: Bot, accid: int, event: AttrDict) -> None:
    msg = event.msg
    if not msg.is_bot and not msg.is_info:
        chat = bot.rpc.get_basic_chat_info(accid, msg.chat_id)
        if chat.chat_type == ChatType.SINGLE:
            bot.rpc.markseen_msgs(accid, [msg.id])
            if msg.text:
                if msg.view_type == ViewType.IMAGE:
                    image = Image.open(msg.file).convert("RGB")
                    image.thumbnail((768, 768))
                else:
                    image = None
                image = pipe(
                    msg.text, ip_adapter_image=image, safety_checker=None
                ).images[0]
                with NamedTemporaryFile(suffix=".png") as tfile:
                    image.save(tfile.name)
                    bot.rpc.send_msg(
                        accid,
                        msg.chat_id,
                        {"file": tfile.name, "quotedMessageId": msg.id},
                    )
            else:
                bot.rpc.send_msg(
                    accid, msg.chat_id, {"text": HELP, "quotedMessageId": msg.id}
                )
    bot.rpc.delete_messages(accid, [msg.id])
