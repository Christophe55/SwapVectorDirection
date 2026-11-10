# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SwapVectorDirection
                                 A QGIS plugin
 Swap Vector Direction permet d'inverser la direction d'un vecteur
                              -------------------
        begin                : 2014-09-17
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Christophe Maginot
        email                : christophe.maginot@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path

from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import (
    Qgis,
    QgsGeometry,
    QgsMultiLineString,
    QgsVectorLayer,
    QgsWkbTypes,
)

MESSAGE_TITLE = 'SwapVectorDirection'


class SwapVectorDirection:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = str(QSettings().value('locale/userLocale') or 'en')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SwapVectorDirection_{}.qm'.format(locale))

        self.translator = None
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr('&Swap Vector Direction')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SwapVectorDirection', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add an action to the QGIS toolbar and/or the Vector menu.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr('Reverse direction of geometry'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            # The action was added with addPluginToVectorMenu(), so it must
            # be removed with removePluginVectorMenu().
            self.iface.removePluginVectorMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        self.actions = []

        if self.translator is not None:
            QCoreApplication.removeTranslator(self.translator)
            self.translator = None

    def _push_message(self, text, level):
        """Display a message in the QGIS message bar."""
        self.iface.messageBar().pushMessage(
            MESSAGE_TITLE, self.tr(text), level=level)

    @staticmethod
    def _reversed_geometry(geom):
        """Return a new QgsGeometry with the direction of the lines reversed.

        :param geom: A line or multiline geometry (2D or 2.5D).
        :type geom: QgsGeometry

        :rtype: QgsGeometry
        """
        if geom.isMultipart():
            multi_line = QgsMultiLineString()
            for part in geom.asGeometryCollection():
                multi_line.addGeometry(part.constGet().reversed())
            return QgsGeometry(multi_line)
        return QgsGeometry(geom.constGet().reversed())

    def run(self):
        """Reverse the direction of the selected features of the layer."""
        layer = self.iface.mapCanvas().currentLayer()

        # Is a layer selected?
        if layer is None:
            self._push_message('No selected Layer', Qgis.Critical)
            return

        # Is it a line or multiline vector layer?
        if (not isinstance(layer, QgsVectorLayer) or
                layer.geometryType() != QgsWkbTypes.LineGeometry):
            self._push_message(
                'The selected layer is not a line or multiline',
                Qgis.Critical)
            return

        # Is at least one feature selected? Otherwise activate select tool.
        if layer.selectedFeatureCount() == 0:
            self._push_message(
                'No selected feature, please, select one and relaunch',
                Qgis.Warning)
            self.iface.actionSelect().trigger()
            return

        # Switch the layer to edit mode. startEditing() returns False when
        # the layer is already being edited, so check isEditable() first.
        if not layer.isEditable() and not layer.startEditing():
            self._push_message(
                'The layer cannot be edited', Qgis.Critical)
            return

        count = 0
        layer.beginEditCommand(self.tr('Swap vector direction'))
        try:
            for feature in layer.selectedFeatures():
                geom = feature.geometry()
                if geom.isNull():
                    continue
                if layer.changeGeometry(
                        feature.id(), self._reversed_geometry(geom)):
                    count += 1
        except Exception:
            layer.destroyEditCommand()
            raise
        layer.endEditCommand()

        # Refresh the map canvas
        self.iface.mapCanvas().refresh()

        self.iface.messageBar().pushMessage(
            MESSAGE_TITLE,
            self.tr("It's done") + ' ({})'.format(count),
            level=Qgis.Info)
