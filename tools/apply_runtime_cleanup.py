#!/usr/bin/env python3
"""One-time cleanup for obsolete Marks result-injector code."""

from pathlib import Path

path = Path("python/gui/mods/mod_under_pressure_marks.py")
text = path.read_text(encoding="utf-8")


def remove_between(value: str, start: str, end: str) -> str:
    start_at = value.index(start)
    end_at = value.index(end, start_at)
    return value[:start_at] + value[end_at:]


text = text.replace("_LINKAGE_RESULTS = 'MarksPanelResults'\n", "")
text = text.replace("_SWF_RESULTS = 'MarksPanelResults.swf'\n", "")
text = remove_between(
    text,
    "class MarksPanelResultsView(MasteryPanelInjectorView):\n",
    "def _registerFlash():\n",
)
text = text.replace(
    "        self._resultInjectorView = None\n"
    "        self._resultPanelReady   = False\n",
    "",
)
text = text.replace("        self._pendingBattleResultProgress = None\n", "")
text = remove_between(
    text,
    "    def _pushBattleResultProgress(self, currentMark, delta):\n",
    "    def _subscribeWindowEvents(self):\n",
)
text = text.replace(
    "        if not provisional:\n"
    "            self._pushBattleResultProgress(value, delta)\n",
    "",
)
text = text.replace(
    "        if self._battleResultsOpen:\n"
    "            self._syncBattleResultProgress()\n",
    "",
)
text = text.replace("            self._syncBattleResultProgress()\n", "")

start = "    def _onBattleResultsWindowChanged(self, isOpen):\n"
end = "    def _restoreHangarPanelAfterResults(self):\n"
start_at = text.index(start)
end_at = text.index(end, start_at)
replacement = """    def _onBattleResultsWindowChanged(self, isOpen):
        self._battleResultsOpen = bool(isOpen)
        logger.debug('battle results window: isOpen=%s', isOpen)
        if isOpen:
            self._hangarVisible = False
            self._lastVisibleState = None
            self._updateVisibility()
        else:
            BigWorld.callback(0.3, self._restoreHangarPanelAfterResults)

"""
text = text[:start_at] + replacement + text[end_at:]

text = remove_between(
    text,
    "    def _injectResultsFlash(self, attempt=0):\n",
    "    def _injectFlash(self, attempt=0):\n",
)
text = text.replace(
    "        elif kind == 'results':\n"
    "            self._resultInjectorView = view\n"
    "            self._resultPanelReady = False\n"
    "            logger.debug('results injector ready')\n",
    "",
)
text = text.replace(
    "        elif view is not None and view == self._resultInjectorView:\n"
    "            self._resultInjectorView = None\n"
    "            self._resultPanelReady = False\n",
    "",
)
text = text.replace(
    "            self._resultInjectorView = None\n"
    "            self._resultPanelReady = False\n",
    "",
)

ready_start = "        if view is not None and view == self._resultInjectorView:\n"
ready_end = "        if view is not None and view is not self._injectorView:\n"
if ready_start in text:
    start_at = text.index(ready_start)
    end_at = text.index(ready_end, start_at)
    text = text[:start_at] + text[end_at:]

obsolete = (
    "_LINKAGE_RESULTS",
    "_SWF_RESULTS",
    "MarksPanelResults",
    "_resultInjectorView",
    "_resultPanelReady",
    "_injectResultsFlash",
    "_pushBattleResultProgress",
    "_syncBattleResultProgress",
    "_pendingBattleResultProgress",
)
remaining = [token for token in obsolete if token in text]
if remaining:
    raise RuntimeError("obsolete result code remains: %s" % ", ".join(remaining))

compile(text, str(path), "exec")
path.write_text(text, encoding="utf-8")

checker = Path("tools/debug_check.py")
checker_text = checker.read_text(encoding="utf-8")
checker_text = checker_text.replace(
    'if "Masters-Marks" in text:',
    'if "Masters" + "-Marks" in text:',
)
checker.write_text(checker_text, encoding="utf-8")
