# ai-automatic-pharmacy-system

## Português

`ai-automatic-pharmacy-system` é um projeto de **IA aplicada a farmácia automática** com foco em duas dores reais:

- ajudar o farmacêutico a decidir o que precisa de intervenção humana;
- ajudar a operação a enxergar quais itens do estoque travam a dispensação.

![Demo da central de farmácia com IA](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/assets/farmacia_ia.jpg)

Em vez de tratar a automação como simples separação de caixas, o projeto assume que uma farmácia inteligente precisa tomar uma decisão segura, explicável e operacionalmente útil antes de liberar um item.

## O que o sistema faz

O sistema lê uma base sintética inspirada em cenários reais de saúde e, para cada prescrição, responde:

- pode seguir para `AUTO_DISPENSE`?
- precisa de `PHARMACIST_REVIEW`?
- deve entrar em `BLOCK`?

Depois disso, ele devolve uma orientação pronta para ação para a equipe farmacêutica e para o estoque.

## Arquitetura funcional

O projeto foi desenhado em três camadas:

### 1. Rules engine

O núcleo decisório é determinístico e auditável. Ele avalia:

- conflito de alergia
- restrição etária
- interação medicamentosa detectada
- interação medicamentosa maior
- duplicidade terapêutica
- estoque insuficiente
- medicamento de alto risco

### 2. Retrieval documental (`RAG-style`)

Depois da decisão, o sistema consulta uma base documental local para recuperar referências úteis sobre:

- alergias
- interações
- pediatria
- duplicidade de classe
- ruptura de estoque
- medicamentos de alto risco
- critérios de dispensação automática segura

Essa camada é **RAG-style**, mas propositalmente leve e local:

- sem dependência de API externa
- sem embeddings obrigatórios
- baseada em retrieval lexical e priorização por tópico

### 3. Explanation layer

Por fim, o projeto monta uma orientação final legível para o time:

- o que aconteceu
- por que aconteceu
- o que o farmacêutico deve fazer
- o que o estoque deve fazer
- quais documentos sustentaram a orientação

## Storytelling do básico ao técnico

Uma farmácia automática não pode ser só rápida. Ela precisa ser segura, rastreável e útil para quem opera a fila real.

Por isso, este MVP foi pensado para transformar uma prescrição em uma **decisão operacional explicável**:

1. recebe pacientes, alergias, prescrições, formulário farmacêutico, interações e estoque;
2. normaliza o medicamento em uma camada `RxNorm-style`;
3. cruza warning farmacêutico `DailyMed-style` e sinais públicos `openFDA-style`;
4. decide com regras clínicas e operacionais;
5. consulta uma base documental local para enriquecer a orientação final;
6. entrega uma fila pronta para triagem, revisão e ação de estoque.

## Bases públicas escolhidas

### Base principal

- [Synthea](https://synthetichealth.github.io/synthea/)

Papel no desenho:

- pacientes sintéticos realistas
- alergias
- backbone de prescrições
- contexto assistencial sem problema de privacidade

### Fontes de enriquecimento

- [RxNorm](https://www.nlm.nih.gov/research/umls/rxnorm/index.html)
- [DailyMed](https://dailymed.nlm.nih.gov/)
- [openFDA](https://open.fda.gov/apis/)

Papel no desenho:

- `RxNorm`: normalização farmacêutica e ingrediente ativo
- `DailyMed`: warning, contraindicação e guidance de uso
- `openFDA`: sinais públicos de risco e criticidade

### Evolução futura

- [MIMIC-IV](https://physionet.org/content/mimiciv/3.0/)

Uso futuro possível:

- validação hospitalar de maior realismo
- administração medicamentosa mais complexa
- benchmark em cenário clínico credenciado

## Dataset local do projeto

O repositório gera automaticamente:

- `patients.csv`
- `allergies.csv`
- `prescriptions.csv`
- `formulary.csv`
- `drug_interactions.csv`
- `inventory.csv`
- `knowledge_base.csv`
- `public_dataset_reference.json`

Essa decisão deixa o projeto:

- reproduzível
- seguro
- portátil
- fácil de publicar no GitHub

## Ferramentas e bibliotecas utilizadas

Ferramentas principais:

- `Python`
- `Streamlit`
- `unittest`

Bibliotecas da standard library usadas no núcleo:

- `csv`
- `json`
- `pathlib`
- `collections.Counter`
- `collections.defaultdict`
- `re`
- `typing`

Arquivos principais:

- [main.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/main.py)
- [streamlit_app.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/streamlit_app.py)
- [src/data_factory.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/src/data_factory.py)
- [src/pipeline.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/src/pipeline.py)
- [src/rag.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/src/rag.py)
- [tests/test_pipeline.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/tests/test_pipeline.py)

## Técnicas utilizadas

### 1. Integração de dados tabulares

O pipeline cruza:

- pacientes
- alergias
- prescrições
- formulário farmacêutico
- interações medicamentosas
- inventário
- base documental local

### 2. Normalização semântica de medicamento

Cada item recebe atributos padronizados, como:

- `rxnorm_code`
- `active_ingredient`
- `therapeutic_class`
- `allergy_group`

### 3. Rule-based clinical decisioning

O motor de decisão é baseado em regras clínicas e operacionais, não em um classificador probabilístico.

Isso foi uma escolha intencional porque, nesse domínio, o núcleo decisório precisa ser:

- auditável
- previsível
- explicável
- fácil de justificar

### 4. Risk scoring heurístico

Cada prescrição recebe um `risk_score` usado para priorização da fila.

Esse score considera pesos para:

- alergia
- interação maior
- restrição etária
- duplicidade terapêutica
- ruptura de estoque
- medicamento de alto risco

### 5. Queue prioritization

As prescrições são convertidas em prioridade operacional:

- `P1`
- `P2`
- `P3`

Isso aproxima o sistema do dia a dia da farmácia, onde não basta classificar: é preciso ordenar trabalho.

### 6. Retrieval documental local

A camada `RAG-style` usa:

- tokenização lexical
- interseção de termos
- bônus por tópico preferencial
- ranking simples de documentos relevantes

Ela não substitui o rules engine. Ela entra **depois** da decisão para enriquecer a orientação.

### 7. Explainable AI

O sistema gera:

- `decision`
- `queue_priority`
- `risk_score`
- `explanation`
- `rag_guidance`
- `stock_guidance`
- `retrieved_titles`
- `retrieved_document_ids`

## Arquitetura

```mermaid
flowchart LR
    A["Synthea-style patients and prescriptions"] --> B["Medication normalization (RxNorm-style)"]
    B --> C["Clinical and operational rules engine"]
    C --> D["DailyMed-style warnings + openFDA-style safety signals"]
    D --> E["Local knowledge base retrieval"]
    E --> F["Actionable guidance for pharmacist and inventory"]
    F --> G["Operational queue with AUTO_DISPENSE / REVIEW / BLOCK"]
```

## Interface de teste

O projeto inclui uma interface local em `Streamlit` desenhada como uma **central operacional de farmácia**.

Ela está organizada em três abas:

- `Triagem farmacêutica`
- `Estoque e reposição`
- `Resumo operacional`

Na prática, a interface permite:

- ver a fila já priorizada
- filtrar por decisão
- abrir uma prescrição específica
- ler uma orientação pronta para ação
- entender o motivo clínico resumido
- ver warning farmacêutico
- acompanhar itens de estoque críticos
- identificar quantas prescrições estão travadas por item
- enxergar o **saldo após a demanda pendente**, e não só o estoque bruto

## Artefatos gerados

- [automatic_pharmacy_report.json](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/data/processed/automatic_pharmacy_report.json)
- [dispense_queue.csv](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/data/processed/dispense_queue.csv)

Colunas relevantes do `dispense_queue.csv`:

- `decision`
- `queue_priority`
- `risk_score`
- `interaction_detected`
- `explanation`
- `rag_guidance`
- `stock_guidance`
- `retrieved_titles`
- `retrieved_document_ids`

## Resultados atuais

- `patient_count = 4`
- `prescription_count = 7`
- `blocked_count = 3`
- `pharmacist_review_count = 3`
- `auto_dispense_count = 1`
- `top_priority_decision = BLOCK`

## Como executar

```bash
python3 main.py
python3 -m unittest discover -s tests -v
python3 -m py_compile main.py streamlit_app.py src/data_factory.py src/pipeline.py src/rag.py tests/test_pipeline.py
streamlit run streamlit_app.py --server.port 8529
```

## Como explicar em entrevista

Versão curta:

> Eu construí um sistema de farmácia automática com IA explicável que combina dados sintéticos inspirados em Synthea, normalização farmacêutica no estilo RxNorm, warnings no estilo DailyMed, sinais de risco inspirados em openFDA e um motor de regras clínicas para decidir se uma prescrição pode ser dispensada automaticamente, precisa de revisão farmacêutica ou deve ser bloqueada.

Versão mais forte:

> Além do rules engine, eu adicionei uma camada documental RAG-style para apoiar a ação humana. Assim, o sistema não apenas classifica a prescrição, mas também devolve uma orientação pronta para o farmacêutico e para a operação de estoque, com rastreabilidade da justificativa.

## Próximos passos possíveis

- trocar o retrieval lexical por embeddings farmacêuticos reais
- acoplar um LLM para reescrever a orientação em linguagem mais natural
- usar FHIR `MedicationRequest` / `MedicationDispense`
- expandir a base de interações
- incluir previsão de ruptura de estoque

## English

`ai-automatic-pharmacy-system` is an AI-driven automatic pharmacy project designed to support both pharmacist triage and inventory operations.

It combines:

- a `Synthea-style` synthetic patient and prescription backbone
- `RxNorm-style` medication normalization
- `DailyMed-style` warning enrichment
- `openFDA-style` safety signals
- a deterministic rules engine
- and a lightweight local `RAG-style` retrieval layer for actionable guidance

The system classifies each prescription into:

- `AUTO_DISPENSE`
- `PHARMACIST_REVIEW`
- `BLOCK`

and then generates an operational guidance layer for pharmacist and stock teams.
