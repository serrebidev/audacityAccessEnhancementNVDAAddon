# __init__.py
# common Part of all of my add-ons
# Copyright 2019-2024 Paulber19
# some parts of code comes from others add-ons:
# add-on Updater (author Joseph Lee)
# brailleExtender (author Andre-Abush )

import addonHandler
import globalVars
import time
import wx
import random
import threading
from logHandler import log
from . import state
state.initialize()
addonHandler.initTranslation()

# keep current update check timer id.
updateChecker = None


def autoUpdateCheck(releaseToDev):
	from . update_check import shouldCheckForUpdate
	if not shouldCheckForUpdate():
		return
	# But not when NVDA itself is updating.
	if globalVars.appArgs.install or globalVars.appArgs.minimal:
		return
	currentTime = int(time.time())
	lastCheck = state.getLastCheck()
	interval = 0 if state.getRemindUpdate() else state.addonUpdateCheckInterval
	whenToCheck = lastCheck + interval
	if currentTime < whenToCheck:
		return
	state.setLastCheck()
	global updateChecker
	if updateChecker is not None:
		updateChecker.Stop()
	# delay before check update (between 20 and 600 secondes, step = 20 seconds)
	r = 20 * random.randint(1, 30)
	updateChecker = wx.CallLater(r * 1000, addonUpdateCheck, True, releaseToDev)


def _runAddonUpdateCheck(auto, releaseToDev):
	from .update_check import CheckForAddonUpdate
	try:
		CheckForAddonUpdate(
			updateInfosFile=None,
			auto=auto,
			releaseToDev=releaseToDev)
	except Exception:
		log.exception("audacityAccessEnhancement: update check failed")


def addonUpdateCheck(auto, releaseToDev):
	global updateChecker
	if updateChecker is not None:
		updateChecker.Stop()
		updateChecker = None
	t = threading.Thread(
		target=_runAddonUpdateCheck,
		args=(auto, releaseToDev),
		name="audacityAccessEnhancementUpdateCheck")
	t.daemon = True
	t.start()
