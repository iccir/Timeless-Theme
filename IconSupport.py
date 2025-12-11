# (c) 2025 Ricci Adams
# MIT License (or) 1-clause BSD License

# Don't evaluate type annotations at runtime
from __future__ import annotations

import sublime
import sublime_plugin
import os
import shutil


FileSuffixToScopeMap = {
    "c":          "source.c",
    "c++":        "source.c++",
    "clojure":    "source.clojure",
    "csharp":     "source.cs",
    "css":        "source.css",
    "go":         "source.go",
    "html":       "text.html.basic, text.html.plain",
    "image":      "binary.image",
    "java":       "source.java",
    "js":         "source.js",
    "json":       "source.json",
    "lisp":       "source.autolisp, source.lisp",
    "lua":        "source.lua",
    "nyx":        "source.js.nyx",
    "objc":       "source.objc",
    "objc++":     "source.objc++",
    "perl":       "source.perl",
    "php":        "embedding.php, source.php",
    "python":     "source.python, text.plain.python",
    "ruby":       "source.ruby, source.shell.ruby, text.plain.rbs, text.plain.ruby",
    "rust":       "source.rust",
    "swift":      "source.swift",
    "typescript": "source.js.typescript, source.ts",
}


CLetterFileSuffixToScopeMap = {
    "h":   "source.c++.header",
    "c":   "source.c",
    "c++": "source.c++",
    "m":   "source.objc",
    "mm":  "source.objc++"
}


AboutTxt = """
This folder was created by the Timeless theme to enable
additional custom file icons.

Due to Sublime Text's implementation of file icons, the
contents of this folder may break icons in other themes.

For more information, visit:
https://github.com/iccir/Timeless-Theme/issues/6
"""


TmPreferencesTemplate = """<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
    <dict>
        <key>scope</key>
        <string>%s</string>
        <key>settings</key>
        <dict>
            <key>icon</key>
            <string>%s</string>
        </dict>
    </dict>
</plist>"""


CPlusPlusHeaderSublimeSyntax = """%YAML 1.2
---
name: C++ Header
scope: source.c++.header
hidden: true

file_extensions:
  - h
  - hh
  - hpp
  - hxx
  - h++

extends: Packages/C++/C++.sublime-syntax
"""


CPlusPlusHeaderSublimeSettings = """{
    "extensions": [ "h" ]
}"""


CPlusPlusSublimeSettings = """{
    /*
        This file was created by the Timeless theme
        to enable the "H" icon for `.h` files. 
    */
    "extensions": [ "__timeless_theme_icon_support__" ]
}"""


def get_timeless_icon_support_path() -> str:
    return os.path.join(sublime.packages_path(), "Timeless Icon Support")


def patch_cpp_extensions(enable: boolean):
    cpp_settings_name = "C++.sublime-settings"
    user_cpp_settings_path = os.path.join(sublime.packages_path(), "User", "C++.sublime-settings")
    magic_key = "__timeless_theme_icon_support__"

    if enable:

        if not os.path.exists(user_cpp_settings_path):
            with open(user_cpp_settings_path, "w") as f:
                f.write(CPlusPlusSublimeSettings)
        else:
            cpp_settings = sublime.load_settings(cpp_settings_name)
            cpp_settings.set("extensions", [ magic_key ])
            sublime.save_settings(cpp_settings_name)

    else:
        cpp_settings = sublime.load_settings(cpp_settings_name)
        if magic_key in cpp_settings.get("extensions", [ ]):
            del cpp_settings["extensions"]
            sublime.save_settings(cpp_settings_name)
            
            # Directly load the JSONC file and see if it is empty.
            # If so, remove it to properly clean up after ourselves.
            raw_dict = sublime.decode_value(sublime.load_resource("Packages/User/C++.sublime-settings"))
            
            if raw_dict == { }:
                os.remove(user_cpp_settings_path)


def install_icon_support(c_letters: bool = False) -> None:
    remove_icon_support()
    
    base_path = get_timeless_icon_support_path()
    files_path = os.path.join(base_path, "files")

    os.mkdir(base_path)
    os.mkdir(files_path)
    
    with open(os.path.join(base_path, "About.txt"), "w") as f:
        f.write(AboutTxt)

    files_to_write = { }
    
    def write_file(path, contents):
        with open(os.path.join(files_path, path), "w") as f:
            f.write(contents)

    for key, value in FileSuffixToScopeMap.items():
        contents = TmPreferencesTemplate % (value, f"file_type_{key}")
        files_to_write[f"icon_{key}.tmPreferences"] = contents
        
    if c_letters:
        for key, value in CLetterFileSuffixToScopeMap.items():
            contents = TmPreferencesTemplate % (value, f"timeless_letter_{key}")
            files_to_write[f"icon_{key}.tmPreferences"] = contents

        write_file("C++ Header.sublime-syntax",   CPlusPlusHeaderSublimeSyntax)
        write_file("C++ Header.sublime-settings", CPlusPlusHeaderSublimeSettings)
        
        patch_cpp_extensions(True)

    for key, value in files_to_write.items():
        write_file(key, value)


def remove_icon_support() -> None:
    try:
        shutil.rmtree(get_timeless_icon_support_path(), ignore_errors=True)
    except:
        pass

    patch_cpp_extensions(False)


class TimelessInstallIconSupport(sublime_plugin.ApplicationCommand):
    def run(self, c_letters: bool = False):
        install_icon_support(c_letters)


class TimelessRemoveIconSupport(sublime_plugin.ApplicationCommand):
    def run(self):
        remove_icon_support()

