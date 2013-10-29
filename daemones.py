#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# daemones 1.0
#
# Copyright (c) 2009-2013 Vita Smid <me@ze.phyr.us>
# Licensed under the terms of The MIT License.


# Feel free to change these constants.
import os
CONFIG = os.path.join(os.environ['HOME'], '.daemones')
#ICON = '/usr/share/icons/Human/16x16/categories/applications-system.png'
ICON = '/usr/share/icons/Humanity/categories/16/applications-system.svg'


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import gobject, gtk, re


class Daemones:
	def readSpecs(self, path):
		'''Parse the config file.'''
		specs = {}
		text = open(path).read()
		# Remove comments.
		text = re.sub('#.*\n', '\n', text)

		for block in text.split('\n\n'):
			# Filter out empty lines.
			lines = filter(None, block.split('\n'))
			# Skip empty blocks.
			if not lines:
				continue
			try:
				name = lines[0]
				spec = {
					'start': lines[1],
					'stop': lines[2],
					'pid': lines[3],
				}
				specs[name] = spec
			except:
				# Faulty specs are ignored.
				pass

		return specs


	def isRunning(self, pidFile):
		return os.path.exists(pidFile)
		''' This doesn't work because many servers don't keep their PID files world-readable.
		try:
			pid = int(open(pidFile).read().strip())
		except:
			return False
		return pid > 1 # It's safe to assume that we're not checking init.
		'''


	def checkDaemons(self):
		return [ (name, self.isRunning(spec['pid'])) for (name, spec) in self.specs.iteritems() ]


	def showMenuCB(self, icon, menu):
		# First update the checkboxes.
		for (specName, status) in self.checkDaemons():
			# A shortcut.
			s = self.specs[specName]
			# The signal handler is blocked so that the automatic update doesn't trigger it.
			# If there's a better way I haven't found it.
			s['item'].handler_block(s['handle'])
			s['item'].set_active(status)
			s['item'].handler_unblock(s['handle'])

		menu.show_all()
		menu.popup(None, None, gtk.status_icon_position_menu, 1, gtk.get_current_event_time(), self.icon)


	def toggleItemCB(self, item, specName):
		cmd = self.specs[specName]['start'] if item.get_active() else self.specs[specName]['stop']
		os.system(cmd)
		self.updateTooltip()


	def updateTooltip(self):
		# Get the list of running daemons.
		up = [ name for (name, status) in self.checkDaemons() if status ]
		tooltip = 'No daemons are running.' if not up else 'Running: %s' % ', '.join(up)
		self.icon.set_tooltip(tooltip)
		return True


	def __init__(self, confPath, iconPath):
		self.specs = self.readSpecs(confPath)

		# Prepare the pop-up menu.
		self.menu = gtk.Menu()
		for specName in sorted(self.specs.keys()):
			menuItem = gtk.CheckMenuItem(specName)
			handle = menuItem.connect('toggled', self.toggleItemCB, specName)
			self.menu.append(menuItem)
			self.specs[specName]['item'] = menuItem
			# Needed for blocking the signal handler (vide showMenuCB).
			self.specs[specName]['handle'] = handle

		# Prepare the icon.
		self.icon = gtk.StatusIcon()
		self.icon.set_from_file(iconPath)
		self.icon.connect('activate', self.showMenuCB, self.menu)


	def main(self):
		'''Run the app.'''
		self.icon.set_visible(True)
		self.updateTooltip()
		# Update the status icon tooltip every 5 seconds.
		gobject.timeout_add(5000, self.updateTooltip)
		gtk.main()


if __name__ == '__main__':
	app = Daemones(CONFIG, ICON)
	app.main()
