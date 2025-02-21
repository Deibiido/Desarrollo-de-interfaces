// -----------------------------
    // Librería para crear las gráficas
    // -----------------------------
    const jocarsaMistyrose = (function () {
        class Chart {
          constructor(containerSelector, data) {
            this.containers = document.querySelectorAll(containerSelector);
            this.data = data;
            this.colors = this.generateColors(data.length);
            this.init();
          }
  
          // Agrega una clase a cada contenedor para estilos
          init() {
            this.containers.forEach(container => {
              container.classList.add("jocarsa-mistyrose");
            });
          }
  
          // Genera una paleta de colores suaves
          generateColors(count) {
            const colors = [];
            const baseHue = Math.random() * 360;
            for (let i = 0; i < count; i++) {
              const hue = (baseHue + (i * 360 / count)) % 360;
              colors.push(`hsl(${hue}, 60%, 70%)`);
            }
            return colors;
          }
  
          // Convierte los valores a porcentajes
          calculatePercentages(data) {
            const total = data.reduce((sum, item) => sum + item.value, 0);
            return data.map(item => ({
              ...item,
              percentage: (item.value / total) * 100
            }));
          }
  
          // Crea un elemento SVG
          createSVG(width, height) {
            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("width", width);
            svg.setAttribute("height", height);
            svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
            return svg;
          }
  
          // Crea un gráfico de pastel
          createPieChart(container) {
            const width = 300;
            const height = 300;
            const radius = Math.min(width, height) / 2 - 20;
  
            const svg = this.createSVG(width, height);
            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
            g.setAttribute("transform", `translate(${width / 2}, ${height / 2})`);
  
            const dataWithPercentages = this.calculatePercentages(this.data);
            let startAngle = 0;
  
            dataWithPercentages.forEach((item, index) => {
              const slice = document.createElementNS("http://www.w3.org/2000/svg", "path");
              const endAngle = startAngle + (item.percentage / 100) * 360;
  
              const x1 = radius * Math.cos((Math.PI * startAngle) / 180);
              const y1 = radius * Math.sin((Math.PI * startAngle) / 180);
              const x2 = radius * Math.cos((Math.PI * endAngle) / 180);
              const y2 = radius * Math.sin((Math.PI * endAngle) / 180);
  
              const largeArcFlag = item.percentage > 50 ? 1 : 0;
  
              const pathData = `
                M 0 0
                L ${x1} ${y1}
                A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}
                Z
              `;
              slice.setAttribute("d", pathData);
              slice.setAttribute("fill", this.colors[index]);
              slice.setAttribute("stroke", "#fff");
              slice.setAttribute("stroke-width", "2");
              slice.setAttribute("data-label", item.label);
              slice.setAttribute("data-percentage", item.percentage.toFixed(2));
              slice.style.transition = "transform 0.2s ease, stroke-width 0.2s ease";
  
              // Efecto hover
              slice.addEventListener("mouseenter", () => {
                slice.setAttribute("stroke-width", "4");
                slice.setAttribute("transform", "scale(1.05)");
              });
              slice.addEventListener("mouseleave", () => {
                slice.setAttribute("stroke-width", "2");
                slice.setAttribute("transform", "scale(1)");
              });
  
              g.appendChild(slice);
  
              // Agrega etiqueta al segmento
              const midAngle = (startAngle + endAngle) / 2;
              const labelRadius = radius * 0.8;
              const labelX = labelRadius * Math.cos((Math.PI * midAngle) / 180);
              const labelY = labelRadius * Math.sin((Math.PI * midAngle) / 180);
  
              const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
              label.setAttribute("x", labelX);
              label.setAttribute("y", labelY);
              label.setAttribute("text-anchor", "middle");
              label.setAttribute("fill", "#333");
              label.setAttribute("font-size", "12px");
              label.setAttribute("font-family", "Arial, sans-serif");
              label.setAttribute("pointer-events", "none");
              label.textContent = `${item.label} (${item.percentage.toFixed(2)}%)`;
  
              g.appendChild(label);
  
              startAngle = endAngle;
            });
  
            svg.appendChild(g);
            container.appendChild(svg);
  
            // Agrega leyenda
            this.createLegend(container, dataWithPercentages);
          }
  
          // Crea un gráfico de barras
          createBarChart(container) {
            const width = 400;
            const height = 300;
            const barWidth = 40;
            const barSpacing = 20;
            const maxValue = Math.max(...this.data.map(item => item.value));
  
            const svg = this.createSVG(width, height);
            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
            g.setAttribute("transform", `translate(50, 20)`);
  
            const dataWithPercentages = this.calculatePercentages(this.data);
  
            dataWithPercentages.forEach((item, index) => {
              const barHeight = (item.value / maxValue) * (height - 50);
              const x = index * (barWidth + barSpacing);
              const y = height - 50 - barHeight;
  
              // Dibuja la barra
              const bar = document.createElementNS("http://www.w3.org/2000/svg", "rect");
              bar.setAttribute("x", x);
              bar.setAttribute("y", y);
              bar.setAttribute("width", barWidth);
              bar.setAttribute("height", barHeight);
              bar.setAttribute("fill", this.colors[index]);
              bar.style.transition = "fill 0.2s ease";
  
              bar.addEventListener("mouseenter", () => {
                bar.setAttribute("fill", "hsl(0, 0%, 80%)");
              });
              bar.addEventListener("mouseleave", () => {
                bar.setAttribute("fill", this.colors[index]);
              });
  
              g.appendChild(bar);
  
              // Etiqueta debajo de la barra
              const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
              label.setAttribute("x", x + barWidth / 2);
              label.setAttribute("y", height - 30);
              label.setAttribute("text-anchor", "middle");
              label.setAttribute("fill", "#333");
              label.setAttribute("font-size", "12px");
              label.setAttribute("font-family", "Arial, sans-serif");
              label.textContent = item.label;
  
              g.appendChild(label);
  
              // Valor sobre la barra
              const value = document.createElementNS("http://www.w3.org/2000/svg", "text");
              value.setAttribute("x", x + barWidth / 2);
              value.setAttribute("y", y - 5);
              value.setAttribute("text-anchor", "middle");
              value.setAttribute("fill", "#333");
              value.setAttribute("font-size", "12px");
              value.setAttribute("font-family", "Arial, sans-serif");
              value.textContent = item.value;
  
              g.appendChild(value);
            });
  
            svg.appendChild(g);
            container.appendChild(svg);
  
            // Agrega leyenda
            this.createLegend(container, dataWithPercentages);
          }
  
          // Crea una leyenda con los datos
          createLegend(container, data) {
            const legend = document.createElement("div");
            legend.style.marginLeft = "20px";
            legend.style.fontFamily = "Arial, sans-serif";
            legend.style.fontSize = "14px";
  
            data.forEach((item, index) => {
              const legendItem = document.createElement("div");
              legendItem.style.display = "flex";
              legendItem.style.alignItems = "center";
              legendItem.style.marginBottom = "8px";
  
              const colorSquare = document.createElement("div");
              colorSquare.style.width = "12px";
              colorSquare.style.height = "12px";
              colorSquare.style.backgroundColor = this.colors[index];
              colorSquare.style.marginRight = "8px";
  
              const labelText = document.createElement("span");
              labelText.textContent = `${item.label}: ${item.value} (${item.percentage ? item.percentage.toFixed(2) + "%" : ""})`;
  
              legendItem.appendChild(colorSquare);
              legendItem.appendChild(labelText);
              legend.appendChild(legendItem);
            });
  
            container.appendChild(legend);
          }
        }
  
        // Exponer la clase Chart
        return {
          Chart: Chart
        };
      })();
  
      // -----------------------------
      // Código para el formulario interactivo
      // -----------------------------
      // Genera dinámicamente los campos según el número de partes indicado
      document.getElementById("generateFields").addEventListener("click", function() {
        const partsCount = parseInt(document.getElementById("partsCount").value);
        const partsFieldsDiv = document.getElementById("partsFields");
        partsFieldsDiv.innerHTML = ""; // Limpiar campos anteriores
  
        for (let i = 0; i < partsCount; i++) {
          const fieldDiv = document.createElement("div");
          const label = document.createElement("label");
          label.textContent = "Valor del trozo " + (i + 1) + ": ";
          const input = document.createElement("input");
          input.type = "number";
          input.min = "0";
          input.value = "0";
          input.classList.add("partValue");
          fieldDiv.appendChild(label);
          fieldDiv.appendChild(input);
          partsFieldsDiv.appendChild(fieldDiv);
        }
      });
  
      // Crea las gráficas con los valores ingresados
      document.getElementById("createGraph").addEventListener("click", function() {
        const partInputs = document.querySelectorAll(".partValue");
        const data = [];
        partInputs.forEach((input, index) => {
          const value = parseFloat(input.value);
          data.push({ label: "Trozo " + (index + 1), value: value });
        });
  
        // Limpiar contenedores de gráficas anteriores
        document.getElementById("pieChartContainer").innerHTML = "";
        document.getElementById("barChartContainer").innerHTML = "";
  
        // Crear gráfica de pastel
        const pieChart = new jocarsaMistyrose.Chart("#pieChartContainer", data);
        pieChart.createPieChart(document.getElementById("pieChartContainer"));
  
        // Crear gráfica de barras
        const barChart = new jocarsaMistyrose.Chart("#barChartContainer", data);
        barChart.createBarChart(document.getElementById("barChartContainer"));
      });
  
      // Genera los campos por defecto al cargar la página (3 partes)
      document.getElementById("generateFields").click();