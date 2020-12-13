$(document).ready(function () {

    const dragContainer = document.querySelector('.drag-container');
    const gridElement = document.querySelector('.grid');
    const filterField = document.querySelector('.grid-control-field.filter-field');
    const searchField = document.querySelector('.grid-control-field.search-field');
    const sortField = document.querySelector('.grid-control-field.sort-field');
    const layoutField = document.querySelector('.grid-control-field.layout-field');
    const itemTemplate = document.querySelector('.grid-item-template');

    function initMuuriSystem() {
        // Reset field values.
        [sortField, filterField, layoutField].forEach((field) => {
            field.value = field.querySelectorAll('option')[0].value;
        });

        // Set inital search query, active filter, active sort value and active layout.
        searchFieldValue = searchField.value.toLowerCase();
        sortFieldValue = sortField.value;

        updateDragState();

        // Search field binding.
        searchField.addEventListener('keyup', function () {
            var newSearch = searchField.value.toLowerCase();
            if (searchFieldValue !== newSearch) {
                searchFieldValue = newSearch;
                filter();
            }
        });

        // Filter, sort and layout bindings.
        filterField.addEventListener('change', filter);
        sortField.addEventListener('change', sort);
        layoutField.addEventListener('change', updateLayout);
    }

    function filter(onFinish = null) {
        const filterFieldValue = filterField.value;
        window.grid.filter(
            (item) => {
                const element = item.getElement();
                const isSearchMatch =
                    !searchFieldValue ||
                    (element.getAttribute('data-title') || '').toLowerCase().indexOf(searchFieldValue) > -1;
                const isFilterMatch =
                    !filterFieldValue || filterFieldValue === element.getAttribute('data-color');
                return isSearchMatch && isFilterMatch;
            },
            {onFinish: onFinish}
        );
    }

    function sort() {
        var currentSort = sortField.value;
        if (sortFieldValue === currentSort) return;

        updateDragState();

        // If we are changing from "order" sorting to something else
        // let's store the drag order.
        if (sortFieldValue === 'order') {
            dragOrder = grid.getItems();
        }

        // Sort the items.
        window.grid.sort(
            currentSort === 'title' ? 'title' : currentSort === 'color' ? 'color title' : dragOrder
        );

        // Update active sort value.
        sortFieldValue = currentSort;
    }

    function updateLayout() {
        const {layout} = grid._settings;
        const val = layoutField.value;
        layout.alignRight = val.indexOf('right') > -1;
        layout.alignBottom = val.indexOf('bottom') > -1;
        layout.fillGaps = val.indexOf('fillgaps') > -1;
        grid.layout();
    }

    function updateDragState() {
        if (sortField.value === 'order') {
            gridElement.classList.add('drag-enabled');
        } else {
            gridElement.classList.remove('drag-enabled');
        }
    }

    $.ajax({
        url: '/get_paints',
    }).done(function (data) {
        if (data['ret']) {
            const elements = [];
            for (let i = 0; i < data['content'].length; i++) {
                if (data['content'][i] !== '') {
                    elements.push(createItemElement(data['content'][i]))
                }
            }

            window.grid = new Muuri('.grid', {
                items: elements,
                showDuration: 400,
                showEasing: 'ease',
                hideDuration: 400,
                hideEasing: 'ease',
                layoutDuration: 400,
                layoutEasing: 'cubic-bezier(0.625, 0.225, 0.100, 0.890)',
                sortData: {
                    title(item, element) {
                        return element.getAttribute('data-title') || '';
                    }
                },
                dragEnabled: true,
                dragHandle: '.grid-card-handle',
                dragContainer: dragContainer,
                dragRelease: {
                    duration: 400,
                    easing: 'cubic-bezier(0.625, 0.225, 0.100, 0.890)',
                    useDragContainer: true,
                },
                dragPlaceholder: {
                    enabled: true,
                    createElement(item) {
                        return item.getElement().cloneNode(true);
                    },
                },
                dragAutoScroll: {
                    targets: [window],
                    sortDuringScroll: false,
                    syncAfterScroll: false,
                },
            });
            initMuuriSystem();
        }
    });

    function createItemElement(paint_file_name) {
        const title = 'Renee Stotijn'
        const width = getRandomInt(1, 2);
        const height = getRandomInt(1, 2);
        const itemElem = document.importNode(itemTemplate.content.children[0], true);
        const background = 'static/images/quadri/' + paint_file_name;

        itemElem.classList.add('h' + height, 'w' + width);
        itemElem.setAttribute('data-title', title);
        itemElem.querySelector('.grid-card-title').innerHTML = title;

        $(itemElem).find('.grid-card').css('background', 'url(' + background + ')')
        $(itemElem).find('.grid-card').css('background-size', 'cover')
        $(itemElem).find('.grid-card').css('background-position', 'center')
        $(itemElem).find('.gallery-caption').attr('href', background);

        return itemElem;
    }

    // https://stackoverflow.com/a/7228322
    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1) + min);
    }

    $('.paint').toFullScreen({
        coeff: .9
    });


})