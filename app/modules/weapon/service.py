from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.weapon.models import Weapon
from app.modules.weapon.schemas import (
    WeaponCreate, 
    WeaponRead, 
    WeaponUpdate, 
    WeaponList  # <- ¡Importante para la paginación!
)
from app.modules.weapon.unit_of_work import WeaponUnitOfWork


class WeaponService:
    """
    Capa de lógica de negocio para Weapons.

    Responsabilidades:
    - Orquestar casos de uso relacionados a armas.
    - Coordinar repositorios mediante WeaponUnitOfWork.
    - Validar reglas de negocio a nivel aplicación.
    - Levantar HTTPException cuando corresponde.
    - NUNCA acceder directamente a la Session.

    REGLA IMPORTANTE — objetos ORM y commit():
    Después de que el UoW hace commit(), SQLAlchemy expira los atributos
    del objeto ORM. Toda serialización (model_dump / model_validate)
    debe ocurrir DENTRO del bloque `with uow:`, antes de que __exit__
    dispare el commit.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el servicio con una sesión de base de datos.

        Args:
            session (Session): Sesión activa utilizada por el UnitOfWork.

        Nota:
            El servicio no maneja directamente la transacción; delega en WeaponUnitOfWork.
        """
        self._session = session

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: WeaponUnitOfWork, weapon_id: int) -> Weapon:
        """
        Obtiene un arma por ID o lanza excepción HTTP 404 si no existe.

        Args:
            uow (WeaponUnitOfWork): Unidad de trabajo activa.
            weapon_id (int): ID del arma.

        Returns:
            Weapon: Instancia encontrada.

        Raises:
            HTTPException: 404 si el arma no existe.
        """
        weapon = uow.weapons.get_by_id(weapon_id)
        if not weapon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Weapon con id={weapon_id} no encontrado",
            )
        return weapon

    # ── Casos de uso ──────────────────────────────────────────────────────────

    def create(self, data: WeaponCreate) -> WeaponRead:
        """
        Crea un nueva arma.

        Flujo:
        - Construye entidad desde DTO
        - Persiste usando repositorio
        - Serializa antes de cerrar la transacción

        Args:
            data (WeaponCreate): Datos de entrada.

        Returns:
            WeaponRead: DTO de salida.
        """
        with WeaponUnitOfWork(self._session) as uow:
            weapon = Weapon.model_validate(data)
            uow.weapons.add(weapon)
            
            result = WeaponRead.model_validate(weapon)

        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> WeaponList:
        """
        Obtiene lista paginada de armas activas.

        Args:
            offset (int): Desplazamiento.
            limit (int): Límite de resultados.

        Returns:
            WeaponList: DTO con lista de armas y total.

        Nota:
            El total se calcula con una query separada.
        """
        with WeaponUnitOfWork(self._session) as uow:
            # Usamos los métodos específicos que filtran por activos
            weapons = uow.weapons.get_active(offset=offset, limit=limit)
            total = uow.weapons.count_model()

            result = WeaponList(
                data=[WeaponRead.model_validate(w) for w in weapons],
                total=total,
            )

        return result

    def get_by_id(self, weapon_id: int) -> WeaponRead:
        """
        Obtiene un arma por ID.

        Args:
            weapon_id (int): ID del arma.

        Returns:
            WeaponRead: DTO del arma.

        Raises:
            HTTPException: 404 si no existe.
        """
        with WeaponUnitOfWork(self._session) as uow:
            weapon = self._get_or_404(uow, weapon_id)
            result = WeaponRead.model_validate(weapon)

        return result

    def update(self, weapon_id: int, data: WeaponUpdate) -> WeaponRead:
        """
        Actualiza un arma existente de forma parcial (PATCH).

        Flujo:
        - Obtiene entidad
        - Aplica cambios dinámicamente
        - Persiste cambios

        Args:
            weapon_id (int): ID del arma.
            data (WeaponUpdate): Datos parciales.

        Returns:
            WeaponRead: DTO actualizado.
        """
        with WeaponUnitOfWork(self._session) as uow:
            weapon = self._get_or_404(uow, weapon_id)

            # Solo campos enviados por el cliente
            patch = data.model_dump(exclude_unset=True)

            for field, value in patch.items():
                setattr(weapon, field, value)

            uow.weapons.add(weapon)
            result = WeaponRead.model_validate(weapon)

        return result

    def soft_delete(self, weapon_id: int) -> None:
        """
        Realiza un borrado lógico del arma.

        Flujo:
        - Obtiene entidad
        - Marca como inactiva
        - Persiste cambio

        Args:
            weapon_id (int): ID del arma.

        Nota:
            No elimina físicamente el registro de la base de datos.
        """
        with WeaponUnitOfWork(self._session) as uow:
            weapon = self._get_or_404(uow, weapon_id)
            weapon.is_active = False
            uow.weapons.add(weapon)