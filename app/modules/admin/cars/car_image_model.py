from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    String,
    ForeignKey,
    func,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class CarImage(Base):
    __tablename__ = "car_images"

    # =======================
    # PRIMARY & FOREIGN KEYS
    # =======================
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_active = Column(Boolean, default=True, index=True)


    car_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cars.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # =======================
    # IMAGE DATA
    # =======================
    image_type = Column(String(30), nullable=False)  # ✅ ADD THIS

    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)

    is_primary = Column(Boolean, default=False, index=True)
    display_order = Column(Integer, default=0, index=True)

    # =======================
    # METADATA
    # =======================
    file_size_kb = Column(Integer, nullable=True)
    content_type = Column(String(50), default="image/jpeg")
    alt_text = Column(String(200), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    # =======================
    # RELATIONSHIP
    # =======================
    car = relationship("Car", back_populates="images")

    # =======================
    # INDEXES
    # =======================
    __table_args__ = (
        Index("idx_car_display_order", "car_id", "display_order"),
        Index("idx_car_primary", "car_id", "is_primary"),
    )

    # =======================
    # METHODS
    # =======================
    def __repr__(self):
        return (
            f"<CarImage id={self.id} "
            f"car_id={self.car_id} "
            f"is_primary={self.is_primary}>"
        )

    def to_dict(self):
        return {
            "id": str(self.id),
            "car_id": str(self.car_id),
            "image_url": self.image_url,
            "thumbnail_url": self.thumbnail_url,
            "is_primary": self.is_primary,
            "display_order": self.display_order,
            "file_size_kb": self.file_size_kb,
            "content_type": self.content_type,
            "alt_text": self.alt_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def file_size_mb(self):
        return round(self.file_size_kb / 1024, 2) if self.file_size_kb else None

    async def mark_as_primary(self, db):
        """
        Mark this image as primary and unmark all other images for the same car.
        """
        from sqlalchemy import update

        await db.execute(
            update(CarImage)
            .where(
                CarImage.car_id == self.car_id,
                CarImage.id != self.id,
                CarImage.is_primary.is_(True),
            )
            .values(is_primary=False)
        )

        self.is_primary = True
