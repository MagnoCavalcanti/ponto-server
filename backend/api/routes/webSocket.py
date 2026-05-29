from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime
from pydantic import ValidationError

from backend.services import ConnectionManager
from backend.schemas import DictDesktop
from backend.database.db_connection import Session
from backend.commands import DesktopContext, get_command

desktop_router = APIRouter(prefix="/ws")

manager = ConnectionManager()


def _get_db():
    return Session()


@desktop_router.websocket("/{empresa}")
async def websocket_endpoint(websocket: WebSocket, empresa: str):
    await manager.connection(empresa, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if not DictDesktop(**data):
                continue

            command_cls = get_command(data["type"])
            if command_cls is None:
                raise ValueError("Valor inesperado no campo 'type'!")

            db = _get_db()
            try:
                context = DesktopContext(
                    empresa=empresa,
                    websocket=websocket,
                    manager=manager,
                    db=db,
                )
                await command_cls().execute(data["payload"], context)
            except KeyError as e:
                await manager.send_exception(
                    websocket, f"o campo {str(e)} é obrigatório!"
                )
            except HTTPException as e:
                await manager.send_exception(websocket, e.detail)
            finally:
                db.close()

    except ValidationError as e:
        print("Erro de validação:", e)
        await websocket.send_json({
            "type": "error",
            "timestamp": datetime.now().isoformat(),
            "payload": {"message": str(e)},
        })
    except ValueError as e:
        await manager.send_exception(websocket, str(e))
    except WebSocketDisconnect:
        manager.disconnection(websocket)
        print("Desconectando...")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        manager.disconnection(websocket)
