window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }

    const productosTable = document.getElementById('productosTable');
    if (productosTable) {
        new simpleDatatables.DataTable(productosTable);
    }

    const lotesProductoTable = document.getElementById('lotesProductoTable');
    if (lotesProductoTable) {
        new simpleDatatables.DataTable(lotesProductoTable);
    }

    const materiaPrimaTable = document.getElementById('materiaPrimaTable');
    if (materiaPrimaTable) {
        new simpleDatatables.DataTable(materiaPrimaTable);
    }

    const entradaMateriaPrimaTable = document.getElementById('entradaMateriaPrimaTable');
    if (entradaMateriaPrimaTable) {
        new simpleDatatables.DataTable(entradaMateriaPrimaTable);
    }
});
