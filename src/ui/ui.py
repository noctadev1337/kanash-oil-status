settings_ui = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>SettingsDialog</class>
 <widget class="QDialog" name="SettingsDialog">
  <property name="windowTitle"><string>Настройки</string></property>
  <property name="minimumSize"><size><width>560</width><height>0</height></size></property>
  <layout class="QVBoxLayout" name="settingsLayout">
   <property name="leftMargin"><number>20</number></property>
   <property name="topMargin"><number>20</number></property>
   <property name="rightMargin"><number>20</number></property>
   <property name="bottomMargin"><number>20</number></property>
   <property name="spacing"><number>16</number></property>
   <item><widget class="QGroupBox" name="fuelGroup">
    <property name="title"><string>Виды топлива</string></property>
    <layout class="QGridLayout" name="fuelLayout">
     <property name="horizontalSpacing"><number>24</number></property>
     <property name="verticalSpacing"><number>8</number></property>
      <item row="0" column="0"><widget class="QCheckBox" name="ai92Check">
       <property name="text"><string>АИ-92</string></property>
      </widget></item>
      <item row="0" column="1"><widget class="QCheckBox" name="ai95Check">
       <property name="text"><string>АИ-95</string></property>
      </widget></item>
      <item row="0" column="2"><widget class="QCheckBox" name="dieselCheck">
       <property name="text"><string>ДТ</string></property>
      </widget></item>
      <item row="1" column="0"><widget class="QCheckBox" name="gasCheck">
       <property name="text"><string>Газ</string></property>
      </widget></item>
      <item row="1" column="1"><widget class="QCheckBox" name="ai98Check">
       <property name="text"><string>АИ-98</string></property>
      </widget></item>
    </layout>
   </widget></item>
   <item><layout class="QFormLayout" name="settingsForm">
    <property name="fieldGrowthPolicy"><enum>QFormLayout::AllNonFixedFieldsGrow</enum></property>
    <property name="horizontalSpacing"><number>16</number></property>
    <property name="verticalSpacing"><number>12</number></property>
    <item row="0" column="0"><widget class="QLabel" name="directoryLabel"><property name="text"><string>Папка результатов:</string></property></widget></item>
    <item row="0" column="1"><layout class="QHBoxLayout" name="directoryLayout">
     <property name="spacing"><number>8</number></property>
     <item><widget class="QLineEdit" name="directory_edit"/></item>
     <item><widget class="QPushButton" name="browse_button">
      <property name="text"><string>Обзор…</string></property>
      <property name="toolTip"><string>Выбрать папку</string></property>
     </widget></item>
    </layout></item>
    <item row="1" column="0"><widget class="QLabel" name="formatLabel"><property name="text"><string>Формат таблицы:</string></property></widget></item>
    <item row="1" column="1"><widget class="QComboBox" name="format_box">
     <item><property name="text"><string>CSV</string></property></item>
     <item><property name="text"><string>XLSX</string></property></item>
    </widget></item>
    <item row="2" column="0"><widget class="QLabel" name="themeLabel"><property name="text"><string>Тема оформления:</string></property></widget></item>
    <item row="2" column="1"><widget class="QComboBox" name="theme_box">
     <item><property name="text"><string>Тёмная</string></property></item>
     <item><property name="text"><string>Светлая</string></property></item>
    </widget></item>
   </layout></item>
   <item><widget class="QLabel" name="error_label">
    <property name="text"><string/></property>
    <property name="wordWrap"><bool>true</bool></property>
   </widget></item>
   <item><layout class="QHBoxLayout" name="buttonsLayout">
    <item><spacer name="buttonsSpacer"><property name="orientation"><enum>Qt::Horizontal</enum></property><property name="sizeHint" stdset="0"><size><width>40</width><height>0</height></size></property></spacer></item>
    <item><widget class="QPushButton" name="cancel_button"><property name="text"><string>Отмена</string></property></widget></item>
    <item><widget class="QPushButton" name="save_button">
     <property name="text"><string>Сохранить</string></property>
     <property name="default"><bool>true</bool></property>
    </widget></item>
   </layout></item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
"""

UI = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1024</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>kanash-oil-status</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout" name="mainLayout" stretch="0,0,1">
    <property name="spacing">
     <number>12</number>
    </property>
    <property name="leftMargin">
     <number>20</number>
    </property>
    <property name="topMargin">
     <number>20</number>
    </property>
    <property name="rightMargin">
     <number>20</number>
    </property>
    <property name="bottomMargin">
     <number>12</number>
    </property>
    <item>
     <layout class="QHBoxLayout" name="topLayout" stretch="1,0">
      <property name="spacing">
       <number>20</number>
      </property>
      <item>
       <layout class="QVBoxLayout" name="controlsLayout">
        <property name="spacing">
         <number>8</number>
        </property>
        <property name="leftMargin">
         <number>0</number>
        </property>
        <property name="topMargin">
         <number>4</number>
        </property>
        <property name="rightMargin">
         <number>0</number>
        </property>
        <property name="bottomMargin">
         <number>0</number>
        </property>
        <item>
         <spacer name="controlsTopSpacer">
          <property name="orientation">
           <enum>Qt::Orientation::Vertical</enum>
          </property>
          <property name="sizeHint" stdset="0">
           <size>
            <width>0</width>
            <height>12</height>
           </size>
          </property>
         </spacer>
        </item>
        <item>
         <widget class="QLabel" name="titleLabel">
          <property name="text">
           <string>Наличие топлива
в Канаше</string>
          </property>
          <property name="alignment">
           <set>Qt::AlignmentFlag::AlignCenter</set>
          </property>
          <property name="wordWrap">
           <bool>true</bool>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QLabel" name="sourceLabel">
          <property name="text">
           <string>Источник данных</string>
          </property>
          <property name="alignment">
           <set>Qt::AlignmentFlag::AlignCenter</set>
          </property>
          <property name="buddy">
           <cstring>sourceBox</cstring>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QComboBox" name="sourceBox">
          <item>
           <property name="text">
            <string>2GIS</string>
           </property>
          </item>
          <item>
           <property name="text">
            <string>T-BANK</string>
           </property>
          </item>
          <item>
           <property name="text">
            <string>SBER</string>
           </property>
          </item>
         </widget>
        </item>
        <item>
         <layout class="QHBoxLayout" name="runButtonsLayout">
          <property name="spacing">
           <number>8</number>
          </property>
          <item>
           <widget class="QPushButton" name="startButton">
            <property name="toolTip">
             <string>Начать парсинг</string>
            </property>
            <property name="text">
             <string>Старт</string>
            </property>
           </widget>
          </item>
          <item>
           <widget class="QPushButton" name="stopButton">
            <property name="enabled">
             <bool>false</bool>
            </property>
            <property name="text">
             <string>Стоп</string>
            </property>
           </widget>
          </item>
         </layout>
        </item>
        <item>
         <widget class="QPushButton" name="settingsButton">
          <property name="text">
           <string>Настройки</string>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QPushButton" name="archiveButton">
          <property name="text">
           <string>Архив отчетов…</string>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QPushButton" name="openTableButton">
          <property name="enabled">
           <bool>false</bool>
          </property>
          <property name="text">
           <string>Открыть таблицу</string>
          </property>
         </widget>
        </item>
        <item>
         <spacer name="controlsSpacer">
          <property name="orientation">
           <enum>Qt::Orientation::Vertical</enum>
          </property>
          <property name="sizeHint" stdset="0">
           <size>
            <width>0</width>
            <height>12</height>
           </size>
          </property>
         </spacer>
        </item>
       </layout>
      </item>
      <item>
       <widget class="QFrame" name="mapFrame">
        <layout class="QVBoxLayout" name="mapLayout">
         <property name="leftMargin">
          <number>0</number>
         </property>
         <property name="topMargin">
          <number>0</number>
         </property>
         <property name="rightMargin">
          <number>0</number>
         </property>
         <property name="bottomMargin">
          <number>0</number>
         </property>
         <item>
          <widget class="QLabel" name="imageLabel">
           <property name="scaledContents">
            <bool>false</bool>
           </property>
           <property name="alignment">
            <set>Qt::AlignmentFlag::AlignCenter</set>
           </property>
          </widget>
         </item>
        </layout>
       </widget>
      </item>
     </layout>
    </item>
    <item>
     <widget class="QLabel" name="logLabel">
      <property name="text">
       <string>Журнал</string>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QTextBrowser" name="logBrowser">
      <property name="minimumSize">
       <size>
        <width>0</width>
        <height>140</height>
       </size>
      </property>
      <property name="placeholderText">
       <string/>
      </property>
      <property name="openLinks">
       <bool>false</bool>
      </property>
     </widget>
    </item>
   </layout>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>1024</width>
     <height>29</height>
    </rect>
   </property>
   <property name="nativeMenuBar">
    <bool>true</bool>
   </property>
   <widget class="QMenu" name="menuFile">
    <property name="title">
     <string>Файл</string>
    </property>
    <addaction name="actionOpen"/>
    <addaction name="actionSave"/>
    <addaction name="actionSaveAs"/>
    <addaction name="separator"/>
    <addaction name="actionArchive"/>
    <addaction name="separator"/>
    <addaction name="actionSettings"/>
    <addaction name="separator"/>
    <addaction name="actionClose"/>
    <addaction name="actionExit"/>
   </widget>
   <widget class="QMenu" name="menuView">
    <property name="title">
     <string>Вид</string>
    </property>
    <addaction name="actionStatusBar"/>
    <addaction name="actionFullScreen"/>
    <addaction name="separator"/>
    <addaction name="actionTheme"/>
   </widget>
   <widget class="QMenu" name="menuParsing">
    <property name="title">
     <string>Парсинг</string>
    </property>
    <widget class="QMenu" name="menuSources">
     <property name="title">
      <string>Источник</string>
     </property>
     <addaction name="actionSource2GIS"/>
     <addaction name="actionSourceTBank"/>
     <addaction name="actionSourceSber"/>
    </widget>
    <addaction name="actionStart"/>
    <addaction name="actionStop"/>
    <addaction name="separator"/>
    <addaction name="menuSources"/>
   </widget>
   <widget class="QMenu" name="menuHelp">
    <property name="title">
     <string>Справка</string>
    </property>
    <addaction name="actionHelp"/>
    <addaction name="separator"/>
    <addaction name="actionAbout"/>
   </widget>
   <addaction name="menuFile"/>
   <addaction name="menuView"/>
   <addaction name="menuParsing"/>
   <addaction name="menuHelp"/>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
  <action name="actionOpen">
   <property name="enabled">
    <bool>false</bool>
   </property>
   <property name="text">
    <string>Открыть отчет…</string>
   </property>
  </action>
  <action name="actionSave">
   <property name="enabled">
    <bool>false</bool>
   </property>
   <property name="text">
    <string>Сохранить отчет</string>
   </property>
  </action>
  <action name="actionSaveAs">
   <property name="enabled">
    <bool>false</bool>
   </property>
   <property name="text">
    <string>Сохранить отчет как…</string>
   </property>
  </action>
  <action name="actionArchive">
   <property name="enabled">
    <bool>false</bool>
   </property>
   <property name="text">
    <string>Архив отчетов…</string>
   </property>
  </action>
  <action name="actionClose">
   <property name="text">
    <string>Закрыть окно</string>
   </property>
  </action>
  <action name="actionExit">
   <property name="text">
    <string>Выйти</string>
   </property>
  </action>
  <action name="actionStatusBar">
   <property name="checkable">
    <bool>true</bool>
   </property>
   <property name="checked">
    <bool>true</bool>
   </property>
   <property name="text">
    <string>Строка состояния</string>
   </property>
  </action>
  <action name="actionFullScreen">
   <property name="checkable">
    <bool>true</bool>
   </property>
   <property name="text">
    <string>Полноэкранный режим</string>
   </property>
  </action>
  <action name="actionSettings">
   <property name="text">
    <string>Настройки…</string>
   </property>
  </action>
  <action name="actionTheme">
   <property name="text">
    <string>Светлая тема</string>
   </property>
  </action>
  <action name="actionStart">
   <property name="text">
    <string>Начать парсинг</string>
   </property>
  </action>
  <action name="actionStop">
   <property name="enabled">
    <bool>false</bool>
   </property>
   <property name="text">
    <string>Остановить парсинг</string>
   </property>
  </action>
  <action name="actionSource2GIS">
   <property name="checkable">
    <bool>true</bool>
   </property>
   <property name="checked">
    <bool>true</bool>
   </property>
   <property name="text">
    <string>2GIS</string>
   </property>
  </action>
  <action name="actionSourceTBank">
   <property name="checkable">
    <bool>true</bool>
   </property>
   <property name="text">
    <string>T-BANK</string>
   </property>
  </action>
  <action name="actionSourceSber">
   <property name="checkable">
    <bool>true</bool>
   </property>
   <property name="text">
    <string>SBER</string>
   </property>
  </action>
  <action name="actionHelp">
   <property name="text">
    <string>Как пользоваться…</string>
   </property>
  </action>
  <action name="actionAbout">
   <property name="text">
    <string>О программе…</string>
   </property>
  </action>
 </widget>
 <resources/>
 <connections/>
</ui>
"""

archive_ui = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>ArchiveDialog</class>
 <widget class="QDialog" name="ArchiveDialog">
  <property name="windowTitle"><string>Архив отчетов</string></property>
  <property name="minimumSize"><size><width>620</width><height>400</height></size></property>
  <layout class="QVBoxLayout" name="archiveLayout">
   <property name="leftMargin"><number>20</number></property>
   <property name="topMargin"><number>20</number></property>
   <property name="rightMargin"><number>20</number></property>
   <property name="bottomMargin"><number>20</number></property>
   <property name="spacing"><number>12</number></property>
   <item><widget class="QLabel" name="archiveLabel"><property name="text"><string>Запуски</string></property></widget></item>
   <item><widget class="QTableWidget" name="table"/></item>
   <item><layout class="QHBoxLayout" name="buttonsLayout">
    <item><spacer name="buttonsSpacer"><property name="orientation"><enum>Qt::Horizontal</enum></property><property name="sizeHint" stdset="0"><size><width>40</width><height>0</height></size></property></spacer></item>
    <item><widget class="QPushButton" name="open_button"><property name="text"><string>Открыть</string></property></widget></item>
    <item><widget class="QPushButton" name="delete_button"><property name="text"><string>Удалить</string></property></widget></item>
    <item><widget class="QPushButton" name="close_button"><property name="text"><string>Закрыть</string></property></widget></item>
   </layout></item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
"""