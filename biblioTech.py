import sys
from sqlalchemy import create_engine, Column, Integer, String, Float, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+psycopg2://library:library@localhost:5433/library"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    copies_available = Column(Integer, nullable=False)
    rental_price = Column(Float, nullable=False)

    # Sécurité supplémentaire côté base de données
    __table_args__ = (
        CheckConstraint("copies_available >= 0", name="ck_copies_positive"),
        CheckConstraint("rental_price >= 0", name="ck_price_positive"),
    )
def validate(title, author, copies, price):
    if not title or not title.strip():
        raise ValueError("Le titre est obligatoire.")
    if not author or not author.strip():
        raise ValueError("L'auteur est obligatoire.")
    if copies < 0:
        raise ValueError("Le nombre d'exemplaires ne peut pas être négatif.")
    if price < 0:
        raise ValueError("Le tarif ne peut pas être négatif.")


def create_book(title, author, copies, price):
    validate(title, author, copies, price)
    with Session() as s:
        book = Book(title=title.strip(), author=author.strip(),
                    copies_available=copies, rental_price=price)
        s.add(book)
        s.commit()
        s.refresh(book)
        return book


def get_book(book_id):
    with Session() as s:
        return s.get(Book, book_id)


def list_books():
    with Session() as s:
        return s.query(Book).order_by(Book.id).all()


def update_book(book_id, title, author, copies, price):
    validate(title, author, copies, price)
    with Session() as s:
        book = s.get(Book, book_id)
        if book is None:
            raise LookupError(f"Livre {book_id} introuvable.")
        book.title, book.author = title.strip(), author.strip()
        book.copies_available, book.rental_price = copies, price
        s.commit()
        return book


def delete_book(book_id):
    with Session() as s:
        book = s.get(Book, book_id)
        if book is None:
            raise LookupError(f"Livre {book_id} introuvable.")
        s.delete(book)
        s.commit()

Base.metadata.create_all(engine)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView,
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BiblioTech - Gestion des livres (monolithe)")
        self.resize(750, 500)
        self.selected_id = None

        # Formulaire
        self.title_in = QLineEdit()
        self.author_in = QLineEdit()
        self.copies_in = QSpinBox()
        self.copies_in.setRange(-1000, 100000)   # on autorise le négatif pour tester la validation
        self.price_in = QDoubleSpinBox()
        self.price_in.setRange(-1000, 100000)
        self.price_in.setDecimals(2)

        form = QFormLayout()
        form.addRow("Titre :", self.title_in)
        form.addRow("Auteur :", self.author_in)
        form.addRow("Exemplaires :", self.copies_in)
        form.addRow("Tarif :", self.price_in)

        # Boutons
        btn_add = QPushButton("Ajouter")
        btn_upd = QPushButton("Modifier")
        btn_del = QPushButton("Supprimer")
        btn_clr = QPushButton("Vider")
        btn_add.clicked.connect(self.on_add)
        btn_upd.clicked.connect(self.on_update)
        btn_del.clicked.connect(self.on_delete)
        btn_clr.clicked.connect(self.clear_form)
        buttons = QHBoxLayout()
        for b in (btn_add, btn_upd, btn_del, btn_clr):
            buttons.addWidget(b)

        # Tableau
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Titre", "Auteur", "Exemplaires", "Tarif"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_select)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self.table)
        self.refresh()

    # --- helpers ---
    def refresh(self):
        books = list_books()
        self.table.setRowCount(len(books))
        for r, b in enumerate(books):
            values = [b.id, b.title, b.author, b.copies_available, b.rental_price]
            for c, v in enumerate(values):
                self.table.setItem(r, c, QTableWidgetItem(str(v)))

    def clear_form(self):
        self.selected_id = None
        self.title_in.clear()
        self.author_in.clear()
        self.copies_in.setValue(0)
        self.price_in.setValue(0)
        self.table.clearSelection()

    def form_values(self):
        return (self.title_in.text(), self.author_in.text(),
                self.copies_in.value(), self.price_in.value())

    def error(self, msg):
        QMessageBox.warning(self, "Erreur", msg)

    # --- slots ---
    def on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        r = rows[0].row()
        self.selected_id = int(self.table.item(r, 0).text())
        self.title_in.setText(self.table.item(r, 1).text())
        self.author_in.setText(self.table.item(r, 2).text())
        self.copies_in.setValue(int(self.table.item(r, 3).text()))
        self.price_in.setValue(float(self.table.item(r, 4).text()))

    def on_add(self):
        try:
            create_book(*self.form_values())
            self.refresh()
            self.clear_form()
        except ValueError as e:
            self.error(str(e))

    def on_update(self):
        if self.selected_id is None:
            return self.error("Sélectionnez un livre dans le tableau.")
        try:
            update_book(self.selected_id, *self.form_values())
            self.refresh()
        except (ValueError, LookupError) as e:
            self.error(str(e))

    def on_delete(self):
        if self.selected_id is None:
            return self.error("Sélectionnez un livre dans le tableau.")
        try:
            delete_book(self.selected_id)
            self.refresh()
            self.clear_form()
        except LookupError as e:
            self.error(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())