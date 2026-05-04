# ai-automatic-pharmacy-system

## Português

`ai-automatic-pharmacy-system` é um projeto de **IA aplicada a farmácia automática** com foco em triagem farmacêutica, segurança medicamentosa e decisão operacional antes da dispensação.

Ele foi desenhado para responder a uma pergunta prática: **o que um sistema de farmácia inteligente precisa validar antes de liberar automaticamente um medicamento?**

Neste projeto, a resposta passa por quatro blocos:

- dados clínicos e prescrições;
- normalização de medicamentos;
- conhecimento farmacêutico estruturado;
- e regras automáticas de segurança e operação.

## Storytelling do básico ao técnico

Uma farmácia automática não deve apenas “separar caixas”. Para ser clinicamente útil e operacionalmente segura, ela precisa checar se a prescrição pode ser dispensada sem risco óbvio e sem criar problema logístico.

Este MVP mostra exatamente esse fluxo:

- recebe prescrições sintéticas no estilo de um ambiente real;
- cruza paciente, alergia e medicamento;
- normaliza o medicamento em uma camada tipo `RxNorm`;
- aplica regras inspiradas em `DailyMed` e sinais de segurança tipo `openFDA`;
- verifica duplicidade terapêutica, interação medicamentosa, restrição etária e estoque;
- e devolve uma decisão final:
  - `AUTO_DISPENSE`
  - `PHARMACIST_REVIEW`
  - `BLOCK`

## Bases públicas escolhidas

### Base principal

- [Synthea](https://synthetichealth.github.io/synthea/)

Por que foi escolhida:

- gera pacientes sintéticos realistas;
- inclui histórico de medicamentos, alergias e encounters;
- é pública, gratuita e sem risco de privacidade;
- é excelente para prototipar sistemas clínicos no GitHub.

### Fontes de enriquecimento

- [RxNorm](https://www.nlm.nih.gov/research/umls/rxnorm/index.html)
- [DailyMed](https://dailymed.nlm.nih.gov/)
- [openFDA](https://open.fda.gov/apis/)

Papel de cada uma:

- `RxNorm`: padronização e normalização de nomes de medicamentos
- `DailyMed`: warnings, contraindicações e trechos de orientação farmacêutica
- `openFDA`: sinais públicos de segurança e farmacovigilância

### Base avançada para evolução futura

- [MIMIC-IV](https://physionet.org/content/mimiciv/3.0/)

Observação:

- `MIMIC-IV` é muito forte para evolução hospitalar real, mas exige credenciamento e treinamento, então não é a melhor escolha para começar rápido no GitHub.

## O que o projeto faz

O pipeline constrói uma fila de dispensação com decisão explicável para cada prescrição.

Regras implementadas:

- conflito de alergia
- restrição etária
- interação medicamentosa maior
- duplicidade terapêutica
- estoque insuficiente
- marcação de medicamento de alto risco

Saídas possíveis:

- `AUTO_DISPENSE`: pode seguir automaticamente
- `PHARMACIST_REVIEW`: precisa de revisão humana
- `BLOCK`: não pode ser liberado automaticamente

## Ferramentas e stack utilizados

Este projeto foi construído propositalmente com um stack simples e reproduzível, para destacar a lógica de negócio e as regras clínicas antes de introduzir dependências mais pesadas.

Ferramentas usadas:

- `Python`
- `csv` da biblioteca padrão para leitura e escrita de datasets tabulares
- `json` da biblioteca padrão para artefatos e metadados do pipeline
- `pathlib` para organização segura dos caminhos do projeto
- `collections.Counter` e `defaultdict` para agregações operacionais
- `unittest` para validação automatizada do comportamento do pipeline
- `Streamlit` para a interface de demonstração local

Arquivos principais do stack:

- [main.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/main.py)
- [streamlit_app.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/streamlit_app.py)
- [src/data_factory.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/src/data_factory.py)
- [src/pipeline.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/src/pipeline.py)
- [tests/test_pipeline.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/tests/test_pipeline.py)

## Topologia do projeto

- [src/data_factory.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/src/data_factory.py)
- [src/pipeline.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/src/pipeline.py)
- [main.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/main.py)
- [tests/test_pipeline.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/tests/test_pipeline.py)

## Arquitetura

```mermaid
flowchart LR
    A["Synthea-style patients and prescriptions"] --> B["Medication normalization (RxNorm-style)"]
    B --> C["Clinical safety rules (DailyMed-style)"]
    C --> D["Safety signal enrichment (openFDA-style)"]
    D --> E["Automatic dispense triage"]
    E --> F["Queue with AUTO_DISPENSE / REVIEW / BLOCK"]
```

## Dataset local do projeto

O repositório gera automaticamente uma base sintética com:

- `patients.csv`
- `allergies.csv`
- `prescriptions.csv`
- `formulary.csv`
- `drug_interactions.csv`
- `inventory.csv`
- `public_dataset_reference.json`

Essa estratégia deixa o projeto:

- reproduzível;
- seguro do ponto de vista de privacidade;
- fácil de executar em qualquer máquina;
- e alinhado a um caso real de Health IT.

## Bases de dados públicas utilizadas no desenho

Embora o runtime local use uma amostra sintética própria para manter o projeto publicável e reproduzível, o desenho do sistema foi baseado nestas fontes públicas:

### 1. Synthea

Fonte:

- [Synthea](https://synthetichealth.github.io/synthea/)

Como foi usada conceitualmente:

- estrutura de pacientes
- histórico medicamentoso
- alergias
- encontros clínicos
- contexto assistencial

No projeto, isso aparece como o **backbone clínico e operacional** da farmácia.

### 2. RxNorm

Fonte:

- [RxNorm](https://www.nlm.nih.gov/research/umls/rxnorm/index.html)

Como foi usada conceitualmente:

- normalização do medicamento
- código de referência farmacêutica
- ingrediente ativo
- classe terapêutica

No projeto, isso aparece como a **camada de padronização farmacêutica**.

### 3. DailyMed

Fonte:

- [DailyMed](https://dailymed.nlm.nih.gov/)

Como foi usada conceitualmente:

- warnings
- contraindicações
- guidance de administração
- trechos de bula e orientação clínica

No projeto, isso aparece como a **camada de conhecimento estruturado para explicabilidade**.

### 4. openFDA

Fonte:

- [openFDA](https://open.fda.gov/apis/)

Como foi usada conceitualmente:

- sinais públicos de segurança
- contagem de eventos adversos
- enriquecimento de criticidade

No projeto, isso aparece como uma **camada complementar de farmacovigilância e risco**.

### 5. MIMIC-IV como evolução futura

Fonte:

- [MIMIC-IV](https://physionet.org/content/mimiciv/3.0/)

Papel no roadmap:

- benchmark hospitalar mais realista
- administração de medicamentos
- validação futura em ambiente clínico de maior complexidade

O projeto não usa `MIMIC-IV` em runtime porque a base exige acesso credenciado, treinamento e acordo de uso.

## Lógica técnica do pipeline

### 1. Backbone clínico

O projeto parte de pacientes e prescrições em um formato inspirado em `Synthea`.

Isso permite simular:

- idade
- setting assistencial
- alergias
- medicação ativa
- refill
- prioridade clínica

### 2. Normalização farmacêutica

Cada medicamento é enriquecido com uma camada `RxNorm-style`:

- `rxnorm_code`
- `active_ingredient`
- `therapeutic_class`
- `allergy_group`

Essa camada é importante porque uma farmácia automática não pode depender apenas do nome textual digitado na prescrição.

### 3. Conhecimento farmacêutico estruturado

O formulário local inclui trechos de warning e idade mínima no estilo de `DailyMed`, além de contagem de sinais públicos no estilo `openFDA`.

Isso permite acoplar:

- warning clínico
- classes terapêuticas
- risco de segurança
- explicabilidade da decisão

## Técnicas utilizadas

Este não é um projeto de deep learning ou NLP pesado. Ele é um projeto de **decision intelligence aplicada à operação farmacêutica**.

As principais técnicas usadas foram:

### 1. Engenharia de dados tabulares

O pipeline organiza e cruza múltiplas tabelas:

- pacientes
- alergias
- prescrições
- formulário de medicamentos
- inventário
- interações medicamentosas

Isso simula um cenário real de integração entre sistemas clínicos, farmacêuticos e operacionais.

### 2. Normalização semântica de medicamento

Cada medicamento recebe atributos padronizados:

- nome canônico
- ingrediente ativo
- classe terapêutica
- código `RxNorm-style`

Essa normalização é importante para evitar que a decisão dependa apenas de texto livre.

### 3. Motor de regras clínicas e operacionais

O núcleo da IA neste MVP é um **rule-based decision engine** explicável.

Ele avalia:

- conflito de alergia
- idade mínima para uso
- interação medicamentosa detectada
- interação maior em nova prescrição
- duplicidade terapêutica
- ruptura ou insuficiência de estoque
- marcação de medicamento de alto risco

### 4. Risk scoring heurístico

Cada prescrição recebe um `risk_score` acumulado a partir de sinais de risco.

Exemplos de pesos:

- alergia: peso muito alto
- interação maior: peso muito alto
- restrição etária: peso alto
- duplicidade terapêutica: peso intermediário
- estoque insuficiente: peso operacional
- medicamento de alto risco: peso complementar

Esse score não é probabilístico; ele é um **score heurístico priorizador**, usado para ordenar a fila de trabalho farmacêutico.

### 5. Triage orientado a filas

O sistema converte a decisão clínica em prioridade operacional:

- `P1`
- `P2`
- `P3`

Isso transforma conhecimento farmacêutico em algo acionável para uma farmácia automática ou central de dispensação.

### 6. Explainable AI / decisão explicável

Em vez de apenas retornar uma classe, o sistema gera:

- decisão final
- score de risco
- regra disparada
- warning farmacêutico
- explicação textual legível

Esse ponto é importante porque, em contexto de saúde, a decisão precisa ser auditável.

### 4. Motor de decisão

Cada prescrição recebe uma pontuação e uma decisão.

Exemplos:

- alergia ao grupo do medicamento → `BLOCK`
- interação maior entre `warfarin` e `ibuprofen` → `BLOCK`
- uso pediátrico abaixo da idade mínima → `BLOCK`
- duplicidade de estatinas → `PHARMACIST_REVIEW`
- estoque insuficiente → `PHARMACIST_REVIEW`
- prescrição estável e segura → `AUTO_DISPENSE`

## Interface de teste

O projeto também inclui uma interface local em `Streamlit` para demonstrar:

- visão geral da fila da farmácia
- filtros por tipo de decisão
- inspeção de uma prescrição específica
- justificativa da decisão
- checagens clínicas e operacionais aplicadas

Arquivo:

- [streamlit_app.py](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/streamlit_app.py)

## Resultados atuais

- `patient_count = 4`
- `prescription_count = 7`
- `blocked_count = 3`
- `pharmacist_review_count = 3`
- `auto_dispense_count = 1`
- `top_priority_decision = BLOCK`

## Artefatos gerados

- [automatic_pharmacy_report.json](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/data/processed/automatic_pharmacy_report.json)
- [dispense_queue.csv](/Users/flaviagaia/Documents/CV_FLAVIA_CODEX/ai-automatic-pharmacy-system/data/processed/dispense_queue.csv)

## Como executar

```bash
python3 main.py
python3 -m unittest discover -s tests -v
python3 -m py_compile main.py src/data_factory.py src/pipeline.py
streamlit run streamlit_app.py --server.port 8529
```

## Como defender o projeto em entrevista

Uma forma boa de explicar:

> Eu modelei um sistema de farmácia automática que usa uma base sintética inspirada em Synthea e a enriquece com conceitos de RxNorm, DailyMed e openFDA para decidir se uma prescrição pode ser dispensada automaticamente, precisa de revisão farmacêutica ou deve ser bloqueada.

## Próximos passos possíveis

- conectar uma interface `Streamlit`
- adicionar RAG farmacêutico para justificativas textuais
- usar FHIR MedicationRequest / MedicationDispense
- plugar uma base maior de interações
- evoluir para previsão de ruptura de estoque

## English

`ai-automatic-pharmacy-system` is an AI-driven automatic pharmacy triage project designed to simulate how a medication dispensing system can validate safety and operational constraints before releasing medication.

It combines:

- a `Synthea-style` synthetic patient and prescription backbone
- `RxNorm-style` medication normalization
- `DailyMed-style` warning and contraindication enrichment
- `openFDA-style` public safety signal enrichment

The pipeline classifies each prescription into:

- `AUTO_DISPENSE`
- `PHARMACIST_REVIEW`
- `BLOCK`

based on allergy conflicts, age restriction, drug-drug interaction, therapeutic duplication, stock shortage, and high-risk medication status.

Technically, the project uses:

- tabular data integration
- medication normalization
- rule-based clinical decisioning
- heuristic risk scoring
- queue prioritization
- explainable decision output
