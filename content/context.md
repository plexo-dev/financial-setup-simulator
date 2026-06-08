Aqui tens um resumo estruturado em formato Markdown ideal para colar num ficheiro README.md ou na documentação do teu repositório (ex.: docs/context.md). Ele servirá como o contexto perfeito para que qualquer agente LLM (ou assistente de IA de código) compreenda o negócio, as regras, as limitações e os objetivos técnicos do projeto.
Contexto do Projeto: Trade SaaS

Este documento serve como fonte de verdade sobre a visão do produto, o modelo de negócio e as diretrizes arquiteturais para orientar o desenvolvimento de software e a geração de código por agentes de IA.
💡 1. A Ideia do Produto

O Trade SaaS é uma plataforma analítica premium, inteligente e de alta performance voltada para traders quantitativos (ou sistemáticos). O objetivo do sistema não é dar recomendações de investimento ou vender robôs prontos , mas sim fornecer a infraestrutura ("as pás e picaretas") para que os próprios investidores desenvolvam, testem e validem estatisticamente as suas teses de investimento.
O Core Funcional do MVP

Para mitigar os riscos iniciais de integração e compliance regulatório, o MVP focar-se-á estritamente em Backtesting (simulação e validação de estratégias com dados do passado).

    Foco temporal: O motor operará puramente com tempos gráficos estruturados de 1 minuto ou mais (1min, 5min, 15min, 1h). Isto desvia o produto da disputa predatória de Alta Frequência (HFT) e latência de microssegundos.

📈 2. Modelo de Negócio e Precificação

O modelo inicial foi pivotado de uma estrutura híbrida para um modelo de SaaS Puro (Cobrança Recorrente Fixa). Como o MVP não possui execução direta de ordens (boletagem) com corretoras, é inviável auditar o lucro real para cobrar taxas de performance nesta fase.
Estrutura de Planos (Pricing Tiers)

A cobrança é feita através de recorrência mensal dividida em três níveis:

    Plano Starter (R$ 29/mês): Recursos limitados e uma taxa de comissão maior sobre simulações ou relatórios exportados.

    Plano Pro (R$ 99/mês): O plano de equilíbrio, desenhado como a principal ferramenta de retenção e conveniência para o utilizador.

    Plano Premium (R$ 199/mês): Funcionalidades totalmente ilimitadas e livre de taxas adicionais.

Processamento Financeiro

    Gateway: Integração com gateways nacionais focados em SaaS (como Asaas ou Iugu).

    Método: Foco total e exclusivo no Pix para maximizar as margens de lucro.

    Fiscal: Emissão automatizada de Notas Fiscais de Serviço (NFS-e) via integrações com ferramentas como e-Notas ou Focus NFe.

🛠️ 3. Arquitetura Técnica & Stack

O projeto adota uma estrutura moderna de Monorepo  focada em performance matemática e isolamento de segurança:

    Backend: Construído em FastAPI (Python) , aproveitando o ecossistema ideal da linguagem para ciência de dados e finanças. Utiliza bibliotecas de alta performance como Pandas, NumPy e vectorbt para processamento vetorizado ultra-rápido de dados históricos.

    Frontend: Interface rica construída em Next.js / React. Apresenta gráficos interativos (via Plotly ou equivalentes) da curva de património (Equity Curve) e painéis de BI com métricas críticas (Drawdown Máximo, Win Rate, Profit Factor). A interface terá um forte apelo visual técnico ("vibe code").

    Banco de Dados: PostgreSQL para o armazenamento de dados estruturados e históricos.

🔒 4. Diretrizes Críticas de Segurança e Compliance
Sandbox de Execução de Código (Crítico)

Os utilizadores escreverão scripts livres em Python através de um editor integrado (Monaco Editor). Por motivos de segurança:

    Isolamento: Cada execução de backtest DEVE ser isolada em containers Docker efêmeros.

    Sanitização: O FastAPI deve bloquear imediatamente a importação de bibliotecas nativas do sistema operativo (ex: os, sys, subprocess) antes da execução.

    FinOps e Estouro de Custos: Devem ser aplicadas travas rígidas de hardware nos containers (limites de CPU/RAM) e timeouts automáticos para evitar loops pesados que escalem os custos de infraestrutura.

Blindagem Jurídica (Regulatório)

Para evitar sanções da CVM e do Banco Central (vender algoritmos fechados ou gerir capital de terceiros sem certificação é ilegal):

    O software deve ser posicionado estritamente como uma calculadora estatística retroativa.

    É obrigatório incluir Termos de Uso explícitos e Disclaimers visíveis reforçando que o simulador reflete dados passados e não garante rentabilidade futura, deixando o risco de mercado 100% sob responsabilidade do utilizador.