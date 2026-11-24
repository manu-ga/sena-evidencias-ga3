"""Segundo enganche: un solo mensaje, sin líneas vacías, con dibujos de animales."""

ANIMALES = "🐶 🐱 🦁 🐼 🐸"

MENSAJE = f"{ANIMALES} ¡Aprende encapsulamiento en Python y protege tus datos! {ANIMALES}"


def segundo_enganche() -> str:
    """Devuelve el mensaje único; nunca vacío."""
    mensaje = MENSAJE.strip()
    if not mensaje:
        raise ValueError("El segundo enganche no puede estar vacío")
    return mensaje


if __name__ == "__main__":
    print(segundo_enganche())
