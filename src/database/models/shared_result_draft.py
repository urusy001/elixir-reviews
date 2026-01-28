from decimal import Decimal
from datetime import datetime
from pathlib import Path
from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class SharedResultDraft(Base):
    __tablename__ = "shared_result_drafts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user: Mapped["User"] = relationship(back_populates="drafts")

    drugs: Mapped[str | None] = mapped_column(Text, nullable=True)
    age: Mapped[int | None] = mapped_column(nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=False, default="Не указан")

    height: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    starting_weight: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    current_weight: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    desired_weight: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    lost_weight: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)

    time_period: Mapped[str | None] = mapped_column(Text, nullable=True)
    course: Mapped[str | None] = mapped_column(Text, nullable=True)

    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    commentary: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    is_submitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    author: Mapped[str] = mapped_column(Text, nullable=False, default="Анонимно")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "gender in ('Не указан','👨 Мужской','👩 Женский')",
            name="ck_shared_result_drafts_gender",
        ),
    )

    @property
    def photos_count(self):
        if (self.photo_url or "").strip() and Path(self.photo_url).exists():
            review_photos_dir = Path(self.photo_url)
            if review_photos_dir.is_dir():
                photos = [p for p in review_photos_dir.iterdir() if p.is_file() and p.suffix == ".jpg"]
                return len(photos)

        return 0

    def __str__(self) -> str:
        age = f"{self.age}" if self.age is not None else "—"
        desired = self.desired_weight if self.desired_weight is not None else "—"
        drugs = (self.drugs or "").strip() or "—"
        time_period = (self.time_period or "").strip() or "—"
        course = (self.course or "").strip() or "—"
        commentary = (self.commentary or "").strip() or "—"
        author = (self.author or "").strip() or "Анонимно"

        return (
            f"ЧЕРНОВИК #{self.id}\n"
            f"💊 Препарат (или несколько): {drugs}\n"
            f"Возраст (по желанию): {age}\n"
            f"Пол: {self.gender}\n"
            f"Рост (см): {self.height or '—'}\n"
            f"Начальный вес (кг): {self.starting_weight or '—'}\n"
            f"Текущий вес (кг): {self.current_weight or '—'}\n"
            f"Желаемый вес (по желанию): {desired}\n"
            f"Сколько всего сброшено кг: {self.lost_weight or '—'}\n"
            f"Период похудения: {time_period}\n"
            f"Курсы/дозировки: {course}\n"
            f"📷 Фото прикреплены: {self.photos_count} шт.\n"
            f"Комментарий (до 2000 символов, опционально): {commentary}\n"
            f"Автор: {author}\n\n"
            f"Обязательные к заполнению поля <b>помечены смайликом</b> ‼️"
        )


    def preview(self) -> str:
        return (
            f"<b>ПРЕДПРОСМОТР ОТЗЫВА #{self.id}</b>\n"
            f"<b>~{self.lost_weight or '—'}кг</b>\n"
            f"{f'<b>Возраст:</b> {self.age or '—'}\n' if self.age is not None else ''}"
            f"<b>Пол:</b> {self.gender or '—'}\n"
            f"\n"
            f"💊 <b>Препарат(ы):</b> {self.drugs or '—'}\n"
            f"💉 <b>Курсы/Дозировки:</b> {self.course or '—'}\n"
            f"\n"
            f"📏 <b>Рост:</b> {self.height or '—'}см\n"
            f"🔽 <b>Старт:</b> {self.starting_weight or '—'}кг\n"
            f"🔽 <b>Сейчас:</b> {self.current_weight or '—'}кг\n"
            f"{f'🏁 <b>Цель:</b> {self.desired_weight or '—'}кг\n' if self.desired_weight is not None else ''}"
            f"⚖️ <b>Сброшено:</b> {self.lost_weight or '—'}кг\n"
            f"🗓️ <b>Период:</b> {self.time_period or '—'}\n"
            f"\n"
            f"{('💬 <b>Комментарий:</b>\n'
                + ((self.commentary or '—') if len(self.commentary) <= 2000 else self.commentary[:1997] + '...')
                + '\n') if self.commentary is not None else ''}"
            f"Автор: {self.author or '—'}"
        )

    def final(self) -> str:
        return (
            f"<b>#{self.id}</b>\n"
            f"<b>~{self.lost_weight}кг</b>\n"
            f"{f'<b>Возраст:</b> {self.age}\n' if self.age is not None else ''}"
            f"<b>Пол:</b> {self.gender}\n"
            f"\n"
            f"💊 <b>Препарат(ы):</b> {self.drugs}\n"
            f"💉 <b>Курсы/Дозировки:</b> {self.course}\n"
            f"\n"
            f"📏 <b>Рост:</b> {self.height}см\n"
            f"🔽 <b>Старт:</b> {self.starting_weight}кг\n"
            f"🔽 <b>Сейчас:</b> {self.current_weight}кг\n"
            f"{f'🏁 <b>Цель:</b> {self.desired_weight}кг\n' if self.desired_weight is not None else ''}"
            f"⚖️ <b>Сброшено:</b> {self.lost_weight}кг\n"
            f"🗓️ <b>Период:</b> {self.time_period}\n"
            f"\n"
            f"{('💬 <b>Комментарий:</b>\n'
                + (self.commentary if len(self.commentary) <= 2000 else self.commentary[:1997] + '...')
                + '\n') if self.commentary else ''}"
            f"Автор: {self.author}\n"
        )