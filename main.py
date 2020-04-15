import codecs
import logging
import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction


logger = logging.getLogger(__name__)


class MyIpExtension(Extension):

    def __init__(self):
        super(MyIpExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    _providers = {
        "opendns": ("@resolver1.opendns.com", "myip.opendns.com", "ANY"),
        "google": ("@ns1.google.com", "o-o.myaddr.l.google.com", "TXT"),
        "akamai": ("@ns1-1.akamaitech.net", "whoami.akamai.net", "ANY")
    }

    def on_event(self, event, extension):
        provider = extension.preferences['provider']
        server, query, qtype = self._providers[provider]
        logger.debug('Querying IP address from %s', server)

        if event.get_keyword() == "ip6":
            version = "-6"
        else:
            version = "-4"

        if provider == "akamai" and version == "-6":
            ip = "Use a different provider for IP6."
        else:
            ip = subprocess.check_output(["dig", server, query, qtype, "+short", version])
            ip = ip.decode("utf-8").strip()
            logger.debug('Got external ip: %s', ip)

        items = [
            ExtensionResultItem(
                icon='images/icon.png',
                name='External IP: %s' % ip,
                description='Press \'enter\' to copy to clipboard.',
                on_enter=CopyToClipboardAction(ip)
            )
        ]

        return RenderResultListAction(items)


if __name__ == '__main__':
    MyIpExtension().run()
