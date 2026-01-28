from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime
from pydantic import ValidationError

import os
import sys

absolut_path = os.path.abspath(os.curdir)
sys.path.insert(0, absolut_path)

from backend.services import ConnectionManager, verificar_empresa
from backend.schemas import DictDesktop
from backend.repositories import FuncionarioRepo, PontoRepo
from backend.database.db_connection import Session

desktop_router = APIRouter(prefix="/ws")

session = Session()


manager = ConnectionManager()

@desktop_router.websocket("/{empresa}")
async def websocket_endpoint(websocket: WebSocket, empresa: str):
     await manager.connection(empresa, websocket)
     try:
          while True:
               data = await websocket.receive_json()
               if DictDesktop(**data):
                    match(data["type"]):
                         case 'punch_record':
                              try:
                                   payload_response = data["payload"]
                                   registers = payload_response["registers"]
                                   repo_register = PontoRepo(session)

                                   repo_register.sync_registers(registers)
                                   await manager.send_personal_message("created", empresa, websocket)

                              except KeyError as e:
                                   await manager.send_exception(websocket, f"o campo {str(e)} é obrigatório!")

                              except HTTPException as e:
                                   await manager.send_exception(websocket, e.detail)
                              
                         case 'employee_sync':
                              payload_response = data['payload']
                              employees = payload_response["employees"]
                              
                              repo_funcionario = FuncionarioRepo(session)
                              repo_funcionario.bulk_insert_funcionario(employees, verificar_empresa(empresa, session))
                              
                         case _:
                              raise ValueError("Valor inesperado no campo 'type'!")
                
            
            
     except ValidationError as e:
                    print("Erro de validação:", e)
                    await websocket.send_json({
                         "type": "error",
                         "timestamp": datetime.now().isoformat(),
                         "payload": {"message": str(e)}
                    })
     except ValueError as e:
          await manager.send_exception(websocket, str(e))
     except WebSocketDisconnect:
          manager.disconnection(websocket)
          print("Desconectando...")
     except Exception as e:
          print(f"Erro inesperado: {e}")
          manager.disconnection(websocket)
        
