# API de Redimensionamento de Imagens

API Flask para processamento de imagens com crops automáticos e redimensionamento para diferentes tamanhos de uniformes.

## 🆕 Novidades na versão 1.3

A API agora suporta **três formas diferentes** de fornecer imagens para processamento:

### 1. 🌐 URL da Imagem (mantido da versão anterior)
```json
POST /process
Content-Type: application/json

{
    "url": "https://exemplo.com/imagem.jpg",
    "tamanhos": {
        "G": 5,
        "M": 10,
        "P FEMININA": 8
    }
}
```

### 2. 📁 Arquivo Local (NOVO)
```json
POST /process
Content-Type: application/json

{
    "local_path": "/caminho/para/imagem.jpg",
    "tamanhos": {
        "GG": 2,
        "G": 3,
        "M": 1
    }
}
```

### 3. 📤 Upload de Arquivo (NOVO)
```bash
POST /process
Content-Type: multipart/form-data

# Campos do formulário:
# - file: arquivo de imagem
# - tamanhos: JSON string com tamanhos e quantidades
```

Exemplo com curl:
```bash
curl -X POST http://localhost:5000/process \
  -F "file=@/caminho/para/imagem.jpg" \
  -F 'tamanhos={"P": 2, "M": 3, "G": 1}'
```

## 📋 Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações da API e documentação |
| `/process` | POST | Processa imagem (URL, local ou upload) |
| `/tamanhos` | GET | Lista tamanhos disponíveis |
| `/crops` | GET | Lista crops disponíveis |
| `/download/<filename>` | GET | Download do arquivo ZIP processado |

## 🎯 Funcionalidades

- ✅ **Preservação de cor**: Mantém o modo de cor original (RGB, CMYK, L, etc.)
- ✅ **Crops automáticos**: MANGA_ESQUERDA, MANGA_DIREITA, FRENTE, COSTAS
- ✅ **Redimensionamento inteligente**: FRENTE e COSTAS são redimensionados para cada tamanho
- ✅ **Texto automático**: Adiciona o nome do tamanho em cada imagem
- ✅ **Múltiplos formatos**: Suporte para PNG, JPG, JPEG, GIF, BMP, TIFF
- ✅ **Download em ZIP**: Todos os arquivos processados em um único arquivo

## 📏 Tamanhos Disponíveis

**Masculino:**
- EXG, XG, GG, G, M, P, PP

**Feminino:**
- EXG FEMININA, XG FEMININA, GG FEMININA, G FEMININA, M FEMININA, P FEMININA, PP FEMININA

**Infantil:**
- 16 ANOS, 14 ANOS, 12 ANOS, 10 ANOS, 8 ANOS, 6 ANOS, 4 ANOS, 2 ANOS

## ✂️ Crops Aplicados

1. **MANGA_ESQUERDA**: (0, 0, 6141.73, 3189.07)
2. **MANGA_DIREITA**: (0, 3493.76, 6141.73, 6682.83)
3. **FRENTE**: (6455.25, 0, 13541.87, 9448.91) - *redimensionado*
4. **COSTAS**: (13855.39, 0, 20942, 9448.91) - *redimensionado*

## 🔧 Como Usar

### 1. Iniciar a API
```bash
python tamanhos.py
```

### 2. Testar com arquivo local
```python
import requests

# Usando arquivo local
payload = {
    "local_path": "C:/caminho/para/imagem.jpg",
    "tamanhos": {"G": 2, "M": 3}
}

response = requests.post(
    "http://localhost:5000/process",
    json=payload
)

print(response.json())
```

### 3. Testar com upload
```python
import requests
import json

# Upload de arquivo
with open('minha_imagem.jpg', 'rb') as file:
    files = {'file': file}
    data = {'tamanhos': json.dumps({"P": 1, "M": 2})}
    
    response = requests.post(
        "http://localhost:5000/process",
        files=files,
        data=data
    )
```

## 📊 Monitoramento de Performance

A API agora monitora:
- 💾 **Uso de memória** em cada etapa
- 🖥️ **Uso de CPU** 
- ⏱️ **Tempo de processamento**
- 📈 **Pico de memória**

## 📁 Estrutura de Arquivos Gerados

```
crop_name_tamanho_quantidade_unidades.jpg/png
```

**Exemplo:**
- `FRENTE_G_5_unidades.jpg`
- `COSTAS_P_FEMININA_3_unidades.png`
- `MANGA_ESQUERDA_GG_2_unidades.jpg`

## ⚠️ Limitações

- **Tamanho máximo**: 500MB por arquivo
- **Formatos suportados**: PNG, JPG, JPEG, GIF, BMP, TIFF
- **Molde fixo**: 20942x9449 pixels

## 🚀 Para Desenvolvedores

Veja o arquivo `exemplo_uso.py` para exemplos práticos de como usar cada forma de entrada da API.

---

**Versão:** 1.3  
**Porto padrão:** 5000  
**Modo de cor:** Preservado do original
