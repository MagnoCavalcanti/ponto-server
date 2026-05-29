from fastapi import WebSocket
from datetime import datetime, date, time

import os
import sys
absolut_path = os.path.abspath(os.curdir)
sys.path.insert(0, absolut_path)

from backend.schemas import Relogio, DictDesktop

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}
        
    async def connection(self, empresa: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[empresa] = websocket
        await self.send_personal_message(
            message="Conexão estabelecida!",
            empresa=empresa,
            websocket= websocket
            )
    
    def disconnection(self, websocket: WebSocket) -> None:
        for empresa, ws in list(self.active_connections.items()):
            if ws is websocket:
                del self.active_connections[empresa]
                break

    async def send_personal_message(self, message: str, empresa: str, websocket: WebSocket) -> None:
        messageJson = {
            "client": empresa
        }
        try:
            msg = DictDesktop(type=message, timestamp=datetime.now().isoformat(), payload=messageJson)
            await websocket.send_json(msg.to_json())
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_req_for_export_registers(self, empresa: str, rep: Relogio, data_inicio: date, data_fim: date) -> None:
        if empresa in self.active_connections.keys():
            try:
                websocket = self.active_connections[empresa]
                message = {
                    "empresa": empresa,
                    "Rep": rep,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim
                }
                await websocket.send_json(message)
                return True
            except Exception as e:
                print(f"Erro ao enviar comando: {e}")

    async def send_exception(self, websocket: WebSocket, message: str):
        if websocket in self.active_connections.values():
            try:
                payload = { "message": message}
                exception_message = DictDesktop(type="error", timestamp=datetime.now().isoformat(), payload=payload)
                json_exception = exception_message.to_json()

                await websocket.send_json(json_exception)
            except Exception as e:
                print(f"Erro inesperado ao lançar a exception: {e}")
        