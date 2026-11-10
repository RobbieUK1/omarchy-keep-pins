import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons as Commons
import qs.Commons
import qs.Ui as Ui

Ui.Panel {
    id: root
    moduleName: "robbie.keep-pins"
    ipcTarget: "robbie.keep-pins"
    property var notes: []
    property string accountPath: "/"
    property double updated: 0
    property double now: Date.now()
    property int selected: 0
    readonly property string pluginDir: decodeURIComponent(String(Qt.resolvedUrl(".")).replace(/^file:\/\//, "").replace(/\/$/, ""))
    readonly property string fontFamily: bar ? bar.fontFamily : Style.font.family
    implicitWidth: label.width + Style.space(18)
    implicitHeight: bar ? bar.barSize : 24
    Commons.Translations { id: strings; directory: Qt.resolvedUrl("i18n") }

    function launch(id) {
        var url = "https://keep.google.com/" + (accountPath === "/" ? "" : accountPath.slice(1))
        if (id && /^local_/.test(id)) {
            url += "?omarchyNote=" + encodeURIComponent(id)
        } else if (id && /^[A-Za-z0-9._-]{1,160}$/.test(id)) url += "#NOTE/" + encodeURIComponent(id)
        Quickshell.execDetached(["omarchy", "launch", "webapp", url])
        close()
    }
    function load(raw) {
        if (raw.length > 3000000) return
        try {
            var data = JSON.parse(raw)
            if (!Array.isArray(data.notes) || data.notes.length > 200) return
            if (typeof data.accountPath !== "string" || !/^\/(?:u\/\d+\/)?$/.test(data.accountPath)) return
            var accepted = data.notes.filter(function(n) {
                return n && typeof n.id === "string" && /^[A-Za-z0-9._-]{1,160}$/.test(n.id)
                    && typeof n.title === "string" && n.title.length <= 500
                    && typeof n.text === "string" && n.text.length <= 12000
            })
            if (accepted.length !== data.notes.length || typeof data.updated !== "number" || !isFinite(data.updated)) return
            notes = accepted
            accountPath = data.accountPath
            updated = Math.min(data.updated * 1000, Date.now())
            selected = 0
        } catch (e) { /* Retain last valid snapshot. */ }
    }
    FileView {
        id: cache
        path: (Quickshell.env("XDG_CACHE_HOME") || Quickshell.env("HOME") + "/.cache") + "/omarchy-keep-pins/notes.json"
        watchChanges: true
        printErrors: false
        onFileChanged: reload()
        onLoaded: root.load(text())
    }
    Timer { interval: 30000; running: root.opened; repeat: true; onTriggered: { root.now = Date.now(); cache.reload() } }
    onOpenedChanged: if (opened) { now = Date.now(); cache.reload() }
    Image {
        id: label
        anchors.centerIn: parent
        source: Qt.resolvedUrl("assets/bulb.svg")
        width: Style.bar.iconFont
        height: Style.bar.iconFont
        fillMode: Image.PreserveAspectFit
        sourceSize.width: Math.ceil(width * 2)
        sourceSize.height: Math.ceil(height * 2)
    }
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.toggle()
        onEntered: if (root.bar) root.bar.showTooltip(root, strings.t("tooltip"))
        onExited: if (root.bar) root.bar.hideTooltip(root)
    }
    Ui.KeyboardPanel {
        id: popup
        anchorItem: root
        owner: root
        bar: root.bar
        open: root.opened
        contentWidth: Style.space(360)
        contentHeight: Math.min(Style.space(540), bodyColumn.implicitHeight + padding * 2)
        focusTarget: keys
        Ui.PanelKeyCatcher {
            id: keys
            anchors.fill: parent
            onCloseRequested: root.close()
            onMoveRequested: function(dx, dy) {
                if (root.notes.length) {
                    root.selected = (root.selected + dy + root.notes.length) % root.notes.length
                    list.positionViewAtIndex(root.selected, ListView.Contain)
                }
            }
            onActivateRequested: if (root.notes.length) root.launch(root.notes[root.selected].id)
            Column {
                id: bodyColumn
                width: parent.width
                spacing: Style.space(10)
                Text {
                    textFormat: Text.PlainText
                    text: strings.t("title")
                    color: Commons.Color.popups.text
                    font.family: root.fontFamily
                    font.pixelSize: Style.font.body
                    font.bold: true
                }
                Row {
                    spacing: Style.space(8)
                    Ui.Button { text: strings.t("open"); onClicked: root.launch("") }
                    Ui.Button {
                        text: strings.t("setup")
                        onClicked: { Quickshell.execDetached(["xdg-open", root.pluginDir + "/SETUP.html"]); root.close() }
                    }
                }
                Text {
                    width: parent.width
                    textFormat: Text.PlainText
                    text: !root.updated ? strings.t("waiting") : root.notes.length ? (root.now - root.updated > 120000 ? strings.t("cached") : strings.t("live")) : strings.t("empty")
                    wrapMode: Text.Wrap
                    color: Commons.Color.popups.text
                    opacity: 0.65
                    font.family: root.fontFamily
                    font.pixelSize: Style.font.caption
                }
                ListView {
                    id: list
                    width: parent.width
                    height: Math.min(contentHeight, Style.space(380))
                    clip: true
                    spacing: Style.space(6)
                    model: root.notes
                    delegate: Rectangle {
                        required property var modelData
                        required property int index
                        width: list.width
                        height: noteColumn.implicitHeight + Style.space(18)
                        radius: Style.cornerRadius
                        color: hover.containsMouse || index === root.selected ? Qt.rgba(Commons.Color.accent.r, Commons.Color.accent.g, Commons.Color.accent.b, 0.16) : "transparent"
                        Column {
                            id: noteColumn
                            x: Style.space(9)
                            y: Style.space(9)
                            width: parent.width - Style.space(18)
                            spacing: Style.space(4)
                            Text {
                                width: parent.width
                                textFormat: Text.PlainText
                                text: modelData.title || strings.t("untitled")
                                color: Commons.Color.popups.text
                                font.family: root.fontFamily
                                font.pixelSize: Style.font.body
                                font.bold: true
                                maximumLineCount: 2
                                wrapMode: Text.Wrap
                                elide: Text.ElideRight
                            }
                            Text {
                                width: parent.width
                                visible: text.length > 0
                                textFormat: Text.PlainText
                                text: modelData.text
                                color: Commons.Color.popups.text
                                opacity: 0.75
                                font.family: root.fontFamily
                                font.pixelSize: Style.font.caption
                                maximumLineCount: 4
                                wrapMode: Text.Wrap
                                elide: Text.ElideRight
                            }
                        }
                        MouseArea {
                            id: hover
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onEntered: root.selected = index
                            onClicked: root.launch(modelData.id)
                        }
                    }
                }
            }
        }
    }
}
