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
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Import des fonctions QGIS
from qgis.core import *
import qgis.utils
# Initialize Qt resources from file resources.py
import sys
import os.path
sys.path.append(os.path.dirname(__file__))
import resources_rc
import os.path
# Import des fonctions d'intreface de Qgis
from qgis.gui import *


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
        
	## initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SwapVectorDirection_{}.qm'.format(locale))
	
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
	
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Swap Vector Direction')

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
        """Add a toolbar icon to the InaSAFE toolbar.

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
            self.iface.addVectorToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SwapVectorDirection/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Reverse direction of geometry'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Swap Vector Direction'),
                action)
            self.iface.removeVectorToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        
        # Inverse le sens de la géométrie des éléments sélectionnés 
        layer = qgis.utils.iface.mapCanvas().currentLayer()
        
        # test si une couche est sélectionnée
        if layer is None:
            qgis.utils.iface.messageBar().pushMessage(u"SwapVectorDirection ", u"No selected Layer", level=QgsMessageBar.CRITICAL)
            return
        
        #teste si au moins une entité est selectionnée, sinon il active 'loutil de selection
        if layer.selectedFeatures() == []:
            qgis.utils.iface.messageBar().pushMessage(u"SwapVectorDirection ", u"No selected feature, please, select one and relaunch", level=QgsMessageBar.WARNING)
            self.iface.actionSelect().trigger()
            #layer.selectedFeatures = QgsMapToolIdentifyFeature(self.iface.mapCanvas(),layer)
            return
            
        layer.startEditing()
        layer.beginEditCommand( "Swap vector direction" )
        
        for feature in layer.selectedFeatures():
            geom = feature.geometry()
            if geom.wkbType() == QGis.WKBMultiLineString:
                nodes = geom.asMultiPolyline()
                for line in nodes:
                    line.reverse()
                newgeom = QgsGeometry.fromMultiPolyline(nodes)
                layer.changeGeometry(feature.id(),newgeom)
                
            elif geom.wkbType() == QGis.WKBLineString:
                nodes = geom.asPolyline()
                nodes.reverse()    
                newgeom = QgsGeometry.fromPolyline(nodes)
                layer.changeGeometry(feature.id(),newgeom)
                
            elif geom.wkbType() == QGis.WKBLineString25D:
                nodes = geom.asPolyline()
                nodes.reverse()    
                newgeom = QgsGeometry.fromPolyline(nodes)
                layer.changeGeometry(feature.id(),newgeom)
                
            elif geom.wkbType() == QGis.WKBMultiLineString25D:
                nodes = geom.asMultiPolyline()
                for line in nodes:
                    line.reverse()
                newgeom = QgsGeometry.fromMultiPolyline(nodes)
                layer.changeGeometry(feature.id(),newgeom)
                
                
            else :
                qgis.utils.iface.messageBar().pushMessage(u"SwapVectorDirection ", u"The selected layer is not a line or multiline", level=QgsMessageBar.CRITICAL)
                return
        
        layer.endEditCommand()
        
        # on rafraichit le canvas
        qgis.utils.iface.mapCanvas().refresh()
        
        #message d'info pour dire que tout s'est bien passé
        qgis.utils.iface.messageBar().pushMessage(u"SwapVectorDirection ", u"It's done", level=QgsMessageBar.INFO)
