# from https://github.com/quarnster/PlatformSettings
# FIXME: discover level? {default, user, syntax, project} with appropriate
#        overriding behavior
# FIXME: platform specific settings at any level clobber project settings

import sublime
import sublime_plugin

class PlatformSettingsEventListener(sublime_plugin.EventListener):
    def check_settings(self, view):
        s = view.settings()
        default_keys = ["plat.${platform}", "plat.${platform}.user",
                        "plat.${platform}.syntax", "plat.${platform}.project",
                        "plat.${platform}.force"]
        keys = s.get("platform_settings_keys", default_keys)
        if not keys:
            keys = default_keys

        s.clear_on_change("platform_settings")

        platform_settings = {}
        for key in keys:
            key = key.replace("${platform}", sublime.platform())
            platform_settings.update(s.get(key, {}) or {})

        for key in platform_settings:
            current = s.get(key, None)
            value = platform_settings.get(key)
            if current != value:
                s.set(key, value)

        def on_change():
            # print("PlatformSettingsEventListener:: on_change (closure)", view)
            self.check_settings(view)

        s.set("platform_settings_was_here", True)
        s.add_on_change("platform_settings",
                        lambda: sublime.set_timeout(on_change, 0))

    def on_activated(self, view):
        # print("PlatformSettingsEventListener:: on_activated")
        self.check_settings(view)

    def on_new(self, view):
        # print("PlatformSettingsEventListener:: on_new")
        self.check_settings(view)

    def on_load(self, view):
        # print("PlatformSettingsEventListener:: on_load")
        self.check_settings(view)
