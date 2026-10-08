# 6 RELATÓRIO COM AS LINHAS DE CÓDIGO DO PROGRAMA

O código completo do AirIA está no repositório do projeto no GitHub (https://github.com/WillXD1000/APS), organizado nas pastas `backend` e `mobile`. Este capítulo apresenta os trechos que implementam as partes centrais do sistema. Os trechos foram copiados sem alteração, e a fonte de cada um indica o arquivo e as linhas de origem.

## 6.1 Cálculo do índice de um poluente

A função abaixo calcula o índice de um único poluente. Ela procura a faixa de concentração em que o valor se encontra e faz uma interpolação linear entre os limites de índice dessa faixa. O índice geral da consulta é o maior entre os poluentes medidos.

Código 1 – Interpolação do índice por poluente

```python
def _indice_por_poluente(poluente: str, concentracao: float) -> int | None:
    """Calcula o índice (0–400) de um único poluente por interpolação linear."""
    faixas = BREAKPOINTS.get(poluente)
    if faixas is None or concentracao is None or concentracao < 0:
        return None

    for conc_min, conc_max, idx_min, idx_max in faixas:
        if conc_min <= concentracao <= conc_max:
            # Interpolação linear dentro da faixa.
            proporcao = (
                (concentracao - conc_min) / (conc_max - conc_min)
                if conc_max > conc_min
                else 0
            )
            return round(idx_min + proporcao * (idx_max - idx_min))

    # Acima da maior faixa: satura no índice máximo.
    return 500
```

Fonte: autoria própria (arquivo `backend/app/services/iqar_service.py`, linhas 85 a 102).


## 6.2 Leitura das medições na OpenAQ

A OpenAQ identifica cada medição pelo sensor que a gerou. O trecho cruza o identificador do sensor com o mapa de sensores da estação para descobrir qual poluente é cada valor, e guarda só os poluentes usados no cálculo.

Código 2 – Associação das medições aos poluentes

```python
        poluentes: dict[str, float] = {}
        for medicao in resp.json().get("results", []):
            valor = medicao.get("value")
            if valor is None:
                continue

            # 1) tenta descobrir o parâmetro pelo sensorsId (caminho principal)
            parametro = None
            sensor_id = medicao.get("sensorsId")
            if sensor_id is not None:
                parametro = mapa_sensores.get(sensor_id)

            # 2) fallback: parâmetro embutido no próprio registro
            if parametro is None:
                parametro = self._extrair_parametro(medicao)

            if parametro in MAPA_PARAMETROS:
                chave = MAPA_PARAMETROS[parametro]
                # Mantém o primeiro valor por poluente (o mais recente).
                poluentes.setdefault(chave, float(valor))

        return poluentes
```

Fonte: autoria própria (arquivo `backend/app/services/openaq_service.py`, linhas 182 a 203).


## 6.3 Integração com o Gemini

A chamada ao Gemini fica dentro de um bloco de tratamento de erros. Se a chamada falhar, o motivo é classificado, registrado no terminal do servidor e usado na mensagem do chat. A consulta, nesse caso, segue com os textos locais.

Código 3 – Classificação do motivo da falha

```python
def classificar_erro(erro: Exception) -> str:
    """Traduz o erro da API em um motivo: cota, modelo, chave ou outro."""
    codigo = getattr(erro, "code", None)
    if codigo == 429:
        return "cota"
    if codigo == 404:
        return "modelo"
    # Chave inválida costuma vir como 400 ("API key not valid"); sem permissão, 401/403.
    if codigo in (401, 403) or (codigo == 400 and "API key" in str(erro)):
        return "chave"
    return "outro"
```

Fonte: autoria própria (arquivo `backend/app/services/gemini_service.py`, linhas 54 a 64).



Código 4 – Chamada ao modelo de linguagem

```python
        try:
            client = self._get_client()
            resposta = client.models.generate_content(
                model=self.modelo,
                contents=prompt,
            )
            texto = (resposta.text or "").strip()
            return texto or None
        except Exception as erro:
            # Qualquer falha cai no fallback, mas o motivo fica registrado.
            self.ultimo_erro = classificar_erro(erro)
            logger.warning(
                "Falha ao chamar o Gemini (modelo=%s, motivo=%s): %s",
                self.modelo,
                self.ultimo_erro,
                str(erro)[:300],
            )
            return None
```

Fonte: autoria própria (arquivo `backend/app/services/gemini_service.py`, linhas 127 a 144).


Antes de chamar a IA, o serviço verifica se já existe uma interpretação recente para o mesmo local, categoria e perfil. O acesso ao cache é protegido por uma trava, porque o servidor atende várias requisições ao mesmo tempo.

Código 5 – Cache das interpretações

```python
        # Reaproveita uma interpretação recente para economizar a cota.
        chave_cache = (local, categoria, perfil_saude)
        agora = time.monotonic()
        with _cache_lock:
            em_cache = _cache_interpretacao.get(chave_cache)
        if em_cache and em_cache[0] > agora:
            return em_cache[1]

        texto = self._gerar(prompt)
        if texto:
            interpretacao, recomendacao = self._separar_partes(texto)
            if interpretacao and recomendacao:
                with _cache_lock:
                    _cache_interpretacao[chave_cache] = (
                        agora + CACHE_INTERPRETACAO_SEGUNDOS,
                        (interpretacao, recomendacao),
                    )
                return interpretacao, recomendacao
```

Fonte: autoria própria (arquivo `backend/app/services/gemini_service.py`, linhas 183 a 200).


## 6.4 Regra de alertas

A regra define o limiar de alerta conforme o perfil, o nível conforme a categoria e o conselho que acompanha a mensagem.

Código 6 – Avaliação do alerta por perfil de saúde

```python
def avaliar_alerta(
    categoria: str | None, perfil_saude: str, cidade: str | None
) -> AvaliacaoAlerta | None:
    """Aplica a regra de alerta. Retorna None quando não há o que alertar."""
    if categoria not in ORDEM_CATEGORIAS:
        return None

    sensivel = perfil_saude in PERFIS_SENSIVEIS
    limiar = "Moderada" if sensivel else "Ruim"
    if ORDEM_CATEGORIAS.index(categoria) < ORDEM_CATEGORIAS.index(limiar):
        return None

    nivel = "perigo" if categoria in ("Muito Ruim", "Péssima") else "atencao"
    local = cidade or "sua região"

    if nivel == "perigo":
        conselho = "Evite sair e, se possível, mantenha as janelas fechadas."
    elif categoria == "Moderada":
        conselho = (
            "Como seu perfil é sensível à poluição, evite esforço físico "
            "prolongado ao ar livre."
        )
    else:
        conselho = "Evite atividades físicas intensas ao ar livre."

    mensagem = f"Qualidade do ar {categoria.lower()} em {local}. {conselho}"
    return AvaliacaoAlerta(nivel=nivel, mensagem=mensagem)
```

Fonte: autoria própria (arquivo `backend/app/services/alert_service.py`, linhas 36 a 62).


## 6.5 Identificação do usuário pelo token

Todas as rotas protegidas usam esta dependência. Ela decodifica o token JWT, verifica a assinatura e a validade e carrega o usuário do banco. Se algo falhar, a requisição é recusada com o código 401.

Código 7 – Dependência de autenticação

```python
def get_usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Extrai e valida o usuário logado a partir do token JWT.

    Levanta 401 se o token for inválido ou o usuário não existir.
    """
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    sub = decodificar_token(token)
    if sub is None:
        raise credenciais_invalidas

    service = AuthService(db)
    usuario = service.buscar_usuario(int(sub))
    if usuario is None:
        raise credenciais_invalidas

    return usuario
```

Fonte: autoria própria (arquivo `backend/app/api/deps.py`, linhas 18 a 41).


## 6.6 Aplicativo

No aplicativo, o cliente HTTP acrescenta o token a todas as requisições, para que as telas não precisem tratar a autenticação.

Código 8 – Inclusão do token nas requisições

```javascript
// Interceptor: adiciona o token (quando houver) no cabeçalho Authorization.
client.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

Fonte: autoria própria (arquivo `mobile/src/api/client.js`, linhas 19 a 26).


A função de localização reúne a permissão, a leitura da posição e o arredondamento das coordenadas que serão enviadas ao servidor.

Código 9 – Obtenção da localização

```javascript
// Retorna { lat, lon, nomeLocal }, com lat/lon já arredondadas para envio.
export async function obterLocalizacao() {
  await garantirPermissao();
  const posicao = await lerPosicao();
  const { latitude, longitude } = posicao.coords;
  return {
    lat: arredondar(latitude),
    lon: arredondar(longitude),
    nomeLocal: await nomeDoLugar(latitude, longitude),
  };
}
```

Fonte: autoria própria (arquivo `mobile/src/services/localizacao.js`, linhas 112 a 122).


Por fim, a tela Início executa o fluxo completo: obtém a localização, consulta o servidor, mostra o resultado e trata separadamente os erros de localização e os erros de comunicação.

Código 10 – Fluxo da tela Início

```javascript
  const atualizar = useCallback(async () => {
    if (ocupadoRef.current) return;
    ocupadoRef.current = true;
    setErro(null);
    setEtapa("localizando");
    try {
      const posicao = await obterLocalizacao();
      setLocal(posicao.nomeLocal);
      setEtapa("consultando");

      const resposta = await consultarQualidadeAr(posicao.lat, posicao.lon);
      setDados(resposta);
      // Popup apenas para alertas novos (o banner aparece sempre).
      if (resposta.alerta?.novo) {
        Alert.alert(tituloDoAlerta(resposta.alerta.nivel), resposta.alerta.mensagem);
      }
    } catch (error) {
      setDados(null);
      if (error instanceof LocalizacaoError) {
        setErro({ tipo: error.tipo, mensagem: error.message });
      } else {
        setErro({ tipo: "api", mensagem: extrairErro(error) });
      }
    } finally {
      setEtapa("pronto");
      ocupadoRef.current = false;
    }
  }, []);
```

Fonte: autoria própria (arquivo `mobile/src/screens/HomeScreen.js`, linhas 48 a 75).
