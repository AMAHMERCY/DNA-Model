 const searchInput = document.getElementById('searchInput');
    const riskFilter = document.getElementById('riskFilter');
    const table = document.getElementById('appointmentsTable');
    const rows = table.getElementsByTagName('tr');

    function filterTable() {
      const searchValue = searchInput.value.toLowerCase();
      const riskValue = riskFilter.value;

      for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        if (cells.length > 0) {
          const name = cells[0].textContent.toLowerCase();
          const risk = cells[3].textContent;

          const matchesSearch = name.includes(searchValue);
          const matchesRisk = !riskValue || risk.includes(riskValue);

          rows[i].style.display = (matchesSearch && matchesRisk) ? '' : 'none';
        }
      }
    }

    searchInput.addEventListener('input', filterTable);
    riskFilter.addEventListener('change', filterTable);
 const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');

    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('show');
      document.getElementById('mainContent').classList.toggle('expanded');
    });