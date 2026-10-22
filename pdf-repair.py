#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib


APP_NAME = "PDF Repair"


def output_filename(source):
    directory = os.path.dirname(source)
    basename = os.path.splitext(os.path.basename(source))[0]

    candidate = os.path.join(
        directory, basename + "_исправленный.pdf"
    )

    number = 1
    while os.path.exists(candidate):
        candidate = os.path.join(
            directory,
            "{}_исправленный_{}.pdf".format(basename, number)
        )
        number += 1

    return candidate


class PDFRepairApp:
    def __init__(self):
        self.window = Gtk.Window(title=APP_NAME)
        self.window.set_default_size(540, 300)
        self.window.set_border_width(18)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("destroy", Gtk.main_quit)

        layout = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )
        self.window.add(layout)

        title = Gtk.Label()
        title.set_markup(
            "<span size='x-large' weight='bold'>"
            "Исправление PDF</span>"
        )
        layout.pack_start(title, False, False, 4)

        self.info = Gtk.Label(
            "Перетащите PDF-файл в это окно\n"
            "или выберите его кнопкой ниже."
        )
        self.info.set_justify(Gtk.Justification.CENTER)
        layout.pack_start(self.info, True, True, 8)

        self.choose_button = Gtk.Button(
            label="Выбрать PDF-файл..."
        )
        self.choose_button.connect(
            "clicked", self.choose_file
        )
        layout.pack_start(self.choose_button, False, False, 0)

        self.status = Gtk.Label(label="Готово к работе")
        self.status.set_line_wrap(True)
        layout.pack_start(self.status, False, False, 4)

        self.progress = Gtk.ProgressBar()
        layout.pack_start(self.progress, False, False, 0)

        targets = [
            Gtk.TargetEntry.new("text/uri-list", 0, 0)
        ]
        self.window.drag_dest_set(
            Gtk.DestDefaults.ALL,
            targets,
            Gdk.DragAction.COPY
        )
        self.window.connect(
            "drag-data-received", self.on_drop
        )

        self.busy = False
        self.window.show_all()

    def choose_file(self, _button):
        dialog = Gtk.FileChooserDialog(
            title="Выберите PDF-файл",
            parent=self.window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "Отмена", Gtk.ResponseType.CANCEL,
            "Открыть", Gtk.ResponseType.ACCEPT
        )

        file_filter = Gtk.FileFilter()
        file_filter.set_name("PDF-файлы")
        file_filter.add_mime_type("application/pdf")
        file_filter.add_pattern("*.pdf")
        file_filter.add_pattern("*.PDF")
        dialog.add_filter(file_filter)

        response = dialog.run()
        filename = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.ACCEPT and filename:
            self.process_file(filename)

    def on_drop(
        self, _widget, context, _x, _y,
        selection_data, _info, timestamp
    ):
        uris = selection_data.get_uris() or []
        accepted = False

        if uris and not self.busy:
            try:
                filename, _host = GLib.filename_from_uri(uris[0])
                if filename and filename.lower().endswith(".pdf"):
                    self.process_file(filename)
                    accepted = True
            except (ValueError, GLib.Error):
                pass

        Gtk.drag_finish(context, accepted, False, timestamp)

    def process_file(self, filename):
        if self.busy:
            return

        if not os.path.isfile(filename):
            self.show_error("Файл не найден.")
            return

        if not filename.lower().endswith(".pdf"):
            self.show_error("Выберите файл с расширением .pdf.")
            return

        gs = shutil.which("gs")
        if not gs:
            self.show_error(
                "Ghostscript не найден.\n"
                "Установите его через пакетный менеджер."
            )
            return

        self.busy = True
        self.choose_button.set_sensitive(False)
        self.progress.pulse()
        self.status.set_text("Обработка PDF...")
        self.info.set_text(os.path.basename(filename))

        threading.Thread(
            target=self.worker,
            args=(filename, gs),
            daemon=True
        ).start()

    def worker(self, filename, gs):
        result = None
        error = None

        try:
            destination = output_filename(filename)

            command = [
                gs,
                "-sDEVICE=pdfwrite",
                "-dPDFSETTINGS=/printer",
                "-dNOPAUSE",
                "-dBATCH",
                "-sOutputFile=" + destination,
                filename
            ]

            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            if completed.returncode != 0:
                details = (completed.stderr or completed.stdout or "")
                raise RuntimeError(
                    "Ghostscript завершился с ошибкой:\n"
                    + details[-2500:]
                )

            if not os.path.isfile(destination):
                raise RuntimeError(
                    "Ghostscript не создал выходной файл."
                )

            if os.path.getsize(destination) == 0:
                raise RuntimeError(
                    "Создан пустой PDF-файл."
                )

            result = destination

            # Открываем результат в PDF Arranger.
            arranger = shutil.which("pdfarranger")
            if not arranger:
                raise RuntimeError(
                    "PDF исправлен, но команда pdfarranger "
                    "не найдена. Файл сохранён:\n" + destination
                )

            subprocess.Popen([arranger, destination])

        except Exception as exc:
            error = str(exc)

        GLib.idle_add(self.finish, result, error)

    def finish(self, result, error):
        self.busy = False
        self.choose_button.set_sensitive(True)
        self.progress.set_fraction(0.0)

        if error:
            self.status.set_text("Ошибка обработки")
            self.show_error(error)
        else:
            self.status.set_text("PDF успешно исправлен")
            self.info.set_text(
                "Создан файл:\n" + os.path.basename(result)
            )

        return False

    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            parent=self.window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Не удалось обработать PDF"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    PDFRepairApp()
    Gtk.main()
