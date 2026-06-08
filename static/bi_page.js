(function () {
    function initBiTooltips(root) {
        if (typeof bootstrap === 'undefined') {
            return;
        }
        const scope = root || document;
        scope.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            bootstrap.Tooltip.getOrCreateInstance(el, {
                trigger: 'hover focus',
                container: 'body',
                customClass: 'bi-metric-tooltip',
            });
        });
    }

    initBiTooltips(document);

    const refreshLink = document.getElementById('biRefreshData');
    const loadingScreen = document.getElementById('loading-screen');
    if (refreshLink && loadingScreen && refreshLink.tagName === 'A') {
        refreshLink.addEventListener('click', function () {
            loadingScreen.style.display = 'flex';
        });
    }

    const chartDataEl = document.getElementById('chart-data');
    if (!chartDataEl) {
        return;
    }

    const chartData = JSON.parse(chartDataEl.textContent);
    const renderAllCharts = Boolean(window.BI_RENDER_ALL_CHARTS);

    if (chartData.risk_scatter) {
        Plotly.newPlot('risk-scatter-chart', chartData.risk_scatter.data, chartData.risk_scatter.layout, { responsive: true });
    }
    if (chartData.risk_score) {
        Plotly.newPlot('risk-score-chart', chartData.risk_score.data, chartData.risk_score.layout, { responsive: true });
    }
    if (chartData.drawdown) {
        Plotly.newPlot('drawdown-chart', chartData.drawdown.data, chartData.drawdown.layout, { responsive: true });
    }
    if (chartData.rolling) {
        Plotly.newPlot('rolling-chart', chartData.rolling.data, chartData.rolling.layout, { responsive: true });
    }
    Plotly.newPlot('benchmark-chart', chartData.benchmark.data, chartData.benchmark.layout, { responsive: true });
    Plotly.newPlot('ibovespa-chart', chartData.ibovespa.data, chartData.ibovespa.layout, { responsive: true });
    Plotly.newPlot('dollar-chart', chartData.dollar.data, chartData.dollar.layout, { responsive: true });
    Plotly.newPlot('comparison-chart', chartData.comparison.data, chartData.comparison.layout, { responsive: true });

    const perTestDrawdown = chartData.per_test_drawdown || {};

    function renderDrawdownChart(testId) {
        const chartEl = document.getElementById('test-dd-chart-' + testId);
        const payload = perTestDrawdown[String(testId)];
        if (!chartEl || !payload || chartEl.dataset.rendered === 'true') {
            return;
        }
        const sDates = payload.strategy.map(function (p) { return p.date; });
        const sDd = payload.strategy.map(function (p) { return p.drawdown_pct; });
        const bDd = (payload.buy_hold || []).map(function (p) { return p.drawdown_pct; });
        Plotly.newPlot('test-dd-chart-' + testId, [
            { x: sDates, y: sDd, mode: 'lines', name: 'Estratégia', line: { color: '#0d6efd', width: 2 } },
            { x: sDates, y: bDd.slice(0, sDates.length), mode: 'lines', name: 'Comprar e manter', line: { color: '#fd7e14', width: 2, dash: 'dash' } },
        ], {
            title: 'Drawdown — ' + payload.title,
            yaxis: { title: 'Drawdown (%)' },
            height: 280,
            margin: { t: 50, b: 40 },
        }, { responsive: true });
        chartEl.dataset.rendered = 'true';
    }

    function renderTestChart(testId) {
        const chartEl = document.getElementById('test-chart-' + testId);
        const dataEl = document.getElementById('test-graph-' + testId);
        if (!chartEl || !dataEl || chartEl.dataset.rendered === 'true') {
            renderDrawdownChart(testId);
            return;
        }
        const graph = JSON.parse(dataEl.textContent);
        Plotly.newPlot('test-chart-' + testId, graph.data, graph.layout, { responsive: true });
        chartEl.dataset.rendered = 'true';
        renderDrawdownChart(testId);
    }

    function renderAllTestCharts() {
        document.querySelectorAll('[id^="test-graph-"]').forEach(function (dataEl) {
            renderTestChart(dataEl.id.replace('test-graph-', ''));
        });
    }

    function expandAccordionPanels(accordionId, parentSelector) {
        const accordion = document.getElementById(accordionId);
        if (!accordion || typeof bootstrap === 'undefined') {
            return Promise.resolve();
        }
        const panels = accordion.querySelectorAll('.accordion-collapse');
        const jobs = Array.from(panels).map(function (panel) {
            panel.removeAttribute('data-bs-parent');
            return bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false }).show();
        });
        return Promise.all(jobs);
    }

    function expandAllSections() {
        const jobs = [
            expandAccordionPanels('algoReferenceAccordion', '#algoReferenceAccordion'),
            expandAccordionPanels('biTestsAccordion', '#biTestsAccordion'),
        ];
        return Promise.all(jobs).then(function () {
            renderAllTestCharts();
        });
    }

    const copyMdButton = document.getElementById('biCopyMarkdown');
    if (copyMdButton) {
        copyMdButton.addEventListener('click', async function () {
            const originalText = copyMdButton.textContent;
            copyMdButton.disabled = true;
            copyMdButton.textContent = 'Copiando…';

            try {
                const response = await fetch('/bi/export/markdown');
                if (!response.ok) {
                    throw new Error('fetch failed');
                }
                const markdown = await response.text();
                await navigator.clipboard.writeText(markdown);
                copyMdButton.textContent = 'Copiado!';
            } catch (error) {
                window.alert('Falha ao copiar. Tente baixar o Markdown.');
                console.error(error);
            } finally {
                window.setTimeout(function () {
                    copyMdButton.disabled = false;
                    copyMdButton.textContent = originalText;
                }, 1500);
            }
        });
    }

    if (renderAllCharts) {
        renderAllTestCharts();
    } else {
        const biAccordion = document.getElementById('biTestsAccordion');
        const biAccordionToggle = document.getElementById('biAccordionToggle');
        if (biAccordion && biAccordionToggle) {
            const biAccordionPanels = biAccordion.querySelectorAll('.accordion-collapse');
            const biAccordionParent = '#biTestsAccordion';
            let biAllExpanded = false;

            function syncBiAccordionToggle() {
                const openCount = biAccordion.querySelectorAll('.accordion-collapse.show').length;
                biAllExpanded = openCount === biAccordionPanels.length;
                biAccordionToggle.textContent = biAllExpanded ? 'Recolher tudo' : 'Expandir tudo';
                biAccordionToggle.setAttribute('aria-expanded', biAllExpanded ? 'true' : 'false');
            }

            biAccordionToggle.addEventListener('click', function () {
                if (biAllExpanded) {
                    biAccordionPanels.forEach(function (panel) {
                        panel.setAttribute('data-bs-parent', biAccordionParent);
                        bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false }).hide();
                    });
                } else {
                    biAccordionPanels.forEach(function (panel) {
                        panel.removeAttribute('data-bs-parent');
                        bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false }).show();
                    });
                    renderAllTestCharts();
                }
                syncBiAccordionToggle();
            });

            biAccordion.addEventListener('shown.bs.collapse', function (event) {
                renderTestChart(event.target.id.replace('test-collapse-', ''));
                initBiTooltips(event.target);
                syncBiAccordionToggle();
            });

            biAccordion.addEventListener('hidden.bs.collapse', syncBiAccordionToggle);

            document.querySelectorAll('#biTestsAccordion .accordion-collapse.show').forEach(function (panel) {
                renderTestChart(panel.id.replace('test-collapse-', ''));
            });
        }

        const algoAccordion = document.getElementById('algoReferenceAccordion');
        const algoAccordionToggle = document.getElementById('algoAccordionToggle');
        if (algoAccordion && algoAccordionToggle) {
            const algoAccordionPanels = algoAccordion.querySelectorAll('.accordion-collapse');
            const algoAccordionParent = '#algoReferenceAccordion';
            let algoAllExpanded = false;

            function syncAlgoAccordionToggle() {
                const openCount = algoAccordion.querySelectorAll('.accordion-collapse.show').length;
                algoAllExpanded = openCount === algoAccordionPanels.length;
                algoAccordionToggle.textContent = algoAllExpanded ? 'Recolher tudo' : 'Expandir tudo';
                algoAccordionToggle.setAttribute('aria-expanded', algoAllExpanded ? 'true' : 'false');
            }

            algoAccordionToggle.addEventListener('click', function () {
                if (algoAllExpanded) {
                    algoAccordionPanels.forEach(function (panel) {
                        panel.setAttribute('data-bs-parent', algoAccordionParent);
                        bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false }).hide();
                    });
                } else {
                    algoAccordionPanels.forEach(function (panel) {
                        panel.removeAttribute('data-bs-parent');
                        bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false }).show();
                    });
                }
                syncAlgoAccordionToggle();
            });

            algoAccordion.addEventListener('shown.bs.collapse', function (event) {
                initBiTooltips(event.target);
                syncAlgoAccordionToggle();
            });
            algoAccordion.addEventListener('hidden.bs.collapse', syncAlgoAccordionToggle);
        }

        const pngButton = document.getElementById('biDownloadPng');
        if (pngButton && typeof html2canvas !== 'undefined') {
            pngButton.addEventListener('click', async function () {
                const originalText = pngButton.textContent;
                pngButton.disabled = true;
                pngButton.textContent = 'Preparando PNG…';

                try {
                    await expandAllSections();
                    await document.fonts.ready;
                    await new Promise(function (resolve) { window.setTimeout(resolve, 800); });

                    const page = document.getElementById('bi-page-content');
                    const plotlyNodes = page.querySelectorAll('.js-plotly-plot');
                    const restores = [];

                    for (const node of plotlyNodes) {
                        const width = node.offsetWidth || 800;
                        const height = node.offsetHeight || 360;
                        const url = await Plotly.toImage(node, {
                            format: 'png',
                            width: width,
                            height: height,
                            scale: 2,
                        });
                        const img = document.createElement('img');
                        img.src = url;
                        img.alt = node.getAttribute('aria-label') || 'Gráfico';
                        img.style.width = width + 'px';
                        img.style.height = height + 'px';
                        img.className = 'bi-export-chart-image';
                        restores.push({ node: node, parent: node.parentNode, img: img });
                        node.parentNode.replaceChild(img, node);
                    }

                    const canvas = await html2canvas(page, {
                        backgroundColor: '#ffffff',
                        scale: 1.5,
                        useCORS: true,
                        logging: false,
                        windowWidth: page.scrollWidth,
                        windowHeight: page.scrollHeight,
                        height: page.scrollHeight,
                        width: page.scrollWidth,
                        scrollX: 0,
                        scrollY: -window.scrollY,
                    });

                    restores.forEach(function (item) {
                        item.parent.replaceChild(item.node, item.img);
                    });

                    initBiTooltips(page);

                    const link = document.createElement('a');
                    const stamp = new Date().toISOString().slice(0, 10);
                    link.download = 'bi_benchmark_' + stamp + '.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                } catch (error) {
                    window.alert('Falha na exportação PNG. Tente baixar o HTML.');
                    console.error(error);
                } finally {
                    pngButton.disabled = false;
                    pngButton.textContent = originalText;
                }
            });
        }
    }
})();
