(function () {
    const chartDataEl = document.getElementById('chart-data');
    if (!chartDataEl) {
        return;
    }

    const chartData = JSON.parse(chartDataEl.textContent);
    const renderAllCharts = Boolean(window.BI_RENDER_ALL_CHARTS);

    Plotly.newPlot('benchmark-chart', chartData.benchmark.data, chartData.benchmark.layout, { responsive: true });
    Plotly.newPlot('ibovespa-chart', chartData.ibovespa.data, chartData.ibovespa.layout, { responsive: true });
    Plotly.newPlot('dollar-chart', chartData.dollar.data, chartData.dollar.layout, { responsive: true });
    Plotly.newPlot('comparison-chart', chartData.comparison.data, chartData.comparison.layout, { responsive: true });

    function renderTestChart(testId) {
        const chartEl = document.getElementById('test-chart-' + testId);
        const dataEl = document.getElementById('test-graph-' + testId);
        if (!chartEl || !dataEl || chartEl.dataset.rendered === 'true') {
            return;
        }
        const graph = JSON.parse(dataEl.textContent);
        Plotly.newPlot('test-chart-' + testId, graph.data, graph.layout, { responsive: true });
        chartEl.dataset.rendered = 'true';
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
                biAccordionToggle.textContent = biAllExpanded ? 'Collapse all' : 'Expand all';
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
                algoAccordionToggle.textContent = algoAllExpanded ? 'Collapse all' : 'Expand all';
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

            algoAccordion.addEventListener('shown.bs.collapse', syncAlgoAccordionToggle);
            algoAccordion.addEventListener('hidden.bs.collapse', syncAlgoAccordionToggle);
        }

        const pngButton = document.getElementById('biDownloadPng');
        if (pngButton && typeof html2canvas !== 'undefined') {
            pngButton.addEventListener('click', async function () {
                const originalText = pngButton.textContent;
                pngButton.disabled = true;
                pngButton.textContent = 'Preparing PNG…';

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
                        img.alt = node.getAttribute('aria-label') || 'Chart';
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

                    const link = document.createElement('a');
                    const stamp = new Date().toISOString().slice(0, 10);
                    link.download = 'bi_benchmark_' + stamp + '.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                } catch (error) {
                    window.alert('PNG export failed. Try downloading HTML instead.');
                    console.error(error);
                } finally {
                    pngButton.disabled = false;
                    pngButton.textContent = originalText;
                }
            });
        }
    }
})();
