(function NorthLight () {

/* Front-end JavaScript for stuartmccall.ca / northlightimages.com
 *
 * Copyright (C) Dylan McCall <www.dylanmccall.com>
 */

$ = jQuery;

var galleries = {};
var filters = {};
var assets = [];

var defaultFilter = undefined;

var SITE_TITLE = document.title;
var SITE_BASE = '/';

var DEFAULT_ASSET_DATA = {
    type: 'image',
    full: {},
    thumb: {}
};


var trackEvent = function(data) {
    window._gaq = window._gaq || [];
    window._gaq.push(data);
};


var onHistoryChange = function() {
    // Check window.history.location for compatibility with devote/HTML5-History-API
    var location = window.history.location || window.location;
    var state = window.history.state;

    var stateFilter = filterForPath(location.pathname);
    selectFilter(stateFilter, state);

    if (stateFilter) {
        $('.nav-menu').val(stateFilter.name);
    } else {
        $('.nav-menu').val('');
    }
};


var pushHistory = function(data, title, url) {
    window.history.pushState(data, title, url);
    onHistoryChange();
};


function Asset(name, data, galleryName) {
    var asset = this;

    var defaultCategories = [];

    if (galleryName) defaultCategories.push(galleryName);

    this.name = name
    this.data = $.extend({'categories' : defaultCategories}, data);
    this.galleryName = galleryName;

    this.mediaType = this.data['media-type'];
    this.link = this.data['link'];

    this.full = this.data['full'] || {};
    this.fullSizes = this.full['sizes'] || [];
    this.fullDefault = this.full['default'] || {};

    this.thumb = this.data['thumb'] || {};
    this.thumbSizes = this.thumb['sizes'] || [];
    this.thumbDefault = this.thumb['default'] || {};

    this.width = this.fullDefault.width;
    this.height = this.fullDefault.height;

    var thumbnailForSize = function(size) {
        var thumbnailName = asset.data.thumbnail || asset.name;

        var thumbnail = $('<a>').attr({
            'role' : 'img button',
            'class' : 'asset',
            'href' : asset.fullDefault.src || asset.link
        }).addClass(asset.mediaType).data('asset', asset);

        $('<div>').attr({
            'class' : 'overlay'
        }).appendTo(thumbnail);

        var srcset = [];

        $.each(asset.thumbSizes, function(index, imgSize) {
            srcset.push(imgSize['src'] + ' ' + imgSize['x']);
        });

        $('<img>').attr({
            'src' : asset.thumbDefault.src,
            'width' : asset.thumbDefault.width,
            'height' : asset.thumbDefault.height,
            'alt' : thumbnailName,
            'srcset': srcset.join(', '),
            'aria-hidden' : 'true'
        }).appendTo(thumbnail);

        return thumbnail;
    };

    var onAssetSelectedCb = function(selectedAsset) {
        if (selectedAsset == asset) {
            asset.thumbnail.addClass('current');
        } else {
            asset.thumbnail.removeClass('current');
            asset.thumbnail.removeClass('loading');
        }
    };

    this.getHeightForWidth = function(maxWidth) {
        var ratio = this.height / this.width;
        var displayWidth = Math.min(this.width, maxWidth);
        var displayHeight = Math.min(displayWidth * ratio, this.height);
        return displayHeight;
    };

    this.refreshView = function(existingView) {
        if (existingView !== undefined && existingView.fitsAsset(this)) {
            return existingView;
        } else if (this.mediaType === 'image') {
            return new ImageAssetView();
        } else if (this.mediaType === 'external-video') {
            return new VideoAssetView();
        }
    };

    var init = function() {
        assetSelectedCbs.push(onAssetSelectedCb);

        asset.thumbnail = thumbnailForSize(80);
        asset.thumbnail.on('click', function(event) {
            event.preventDefault();
        });
    };

    init();
}


function AssetView() {
    var assetView = this;

    this.contentBox = $('<div>')
        .addClass('asset-content')
        .data('asset-view', this);
    var content = undefined;

    this.fitsAsset = function(asset) {
        return false;
    };

    this.getHeightForAsset = function(asset, container) {
        return asset.getHeightForWidth(container.innerWidth());
    };

    this.display = function(asset) {
        if (content === undefined) {
            content = this.createContent(asset);
        } else {
            content = this.updateContent(asset, content);
        }
    };

    this.remove = function() {
        this.contentBox.empty();
        content = undefined;
    };
}


function ImageAssetView() {
    var imageAssetView = this;

    this.contentBox.addClass('asset-image');

    this.fitsAsset = function(asset) {
        return asset.mediaType === 'image';
    };

    this.createContent = function(asset) {
        var content = $('<img>')
            .addClass('loading')
            .on('load', onImgLoaded)
            .appendTo(this.contentBox);

        updateImgWithAsset(content, asset)
        loadingAsset(asset, true, imageAssetView);

        return content;
    };

    this.updateContent = function(asset, content) {
        content.addClass('fadeout');
        setTimeout(function() {
            content.remove();
        }, 1000);
        return this.createContent(asset);
    };

    var updateImgWithAsset = function(img, asset) {
        var srcset = [];

        $.each(asset.fullSizes, function(index, imgSize) {
            srcset.push(imgSize['src'] + ' ' + imgSize['x']);
        });

        img.attr({
            'src' : asset.fullDefault.src,
            'width' : asset.fullDefault.width,
            'height' : asset.fullDefault.height,
            'alt': '',
            'srcset': srcset.join(', ')
        });

        img.data('asset', asset);
    };

    var onImgLoaded = function(event) {
        asset = $(this).data('asset');
        $(this).removeClass('loading');
        if (asset) loadedAsset(asset, imageAssetView);
    };
}
ImageAssetView.prototype = new AssetView();


function VideoAssetView() {
    var videoAssetView = this;

    this.contentBox.addClass('asset-external-video');

    var player = undefined;
    var playerReady = false;
    var playerVideo = undefined;

    var currentAsset = undefined;

    this.fitsAsset = function(asset) {
        return asset.mediaType === 'external-video';
    };

    this.createContent = function(asset) {
        var playerElem = $('<div>')
            .addClass('player')
            .appendTo(this.contentBox)
            .css({'visibility' : 'hidden'});

        doWhenYouTubeIsReady(function() {
            player = new window.YT.Player(playerElem[0], {
                'width': asset.fullDefault.width,
                'height': asset.fullDefault.height,
                'videoId': asset.fullDefault.videoId,
                'playerVars': {
                    'autoplay': 0,
                    'autohide': 1,
                    'controls': 1,
                    'disablekb' : 1,
                    'enablejsapi': 1,
                    'rel': 0,
                    'showinfo': 0,
                    'suggestedQuality':'large',
                    'modestbranding': 0,
                    'theme' : 'dark'
                },
                'events': {
                    'onReady': onPlayerReady
                }
            });
        });

        loadedAsset(selectedAsset, videoAssetView);
        return playerElem;
    };

    this.updateContent = function(asset, content) {
        this.videoSelected(asset);
        loadedAsset(asset, videoAssetView);
        return content;
    };

    var onPlayerReady = function() {
        playerReady = true;
        if (selectedAsset) videoAssetView.videoSelected(selectedAsset);
        loadedAsset(selectedAsset, videoAssetView);
        $(player.getIframe()).css({'visibility' : 'visible'})
    };

    this.videoSelected = function(asset) {
        if (!playerReady) return;

        var previousState = player.getPlayerState();

        var wasPlaying = (previousState == 0 || previousState == 1 || previousState == 3);

        if (wasPlaying) {
            player.loadVideoById(asset.fullDefault.videoId, 0, 'large');
        } else  {
            player.cueVideoById(asset.fullDefault.videoId, 0, 'large');
        }

        player.setSize(asset.fullDefault.width, asset.fullDefault.height);

        playerVideo = asset;
    };
}
VideoAssetView.prototype = new AssetView();


function ViewerBox(container) {
    var viewerBox = this;

    container = $(container);

    var contentWrapper = $('.viewer-content-wrapper', container);
    var captionBox = $('.caption', container);

    var assetView = undefined;

    var hide = function() {
        container.stop(true, false).animate({
            'opacity' : 0
        }, 150, function() {
            container.hide();
            container.removeClass('loading');
            if (assetView !== undefined) {
                assetView.remove();
                assetView = undefined;
            }
        });

        contentWrapper.stop(true, false);
        contentWrapper.animate({
            'min-height' : 0,
            'height' : 0
        }, {
            'duration' : 150,
            'complete' : function() {
                changedLayout();
            }
        });
    };

    var showAsset = function(asset, replaceExisting) {
        if (replaceExisting === undefined) replaceExisting = true;

        container.stop(true, false).show().animate({
            'opacity' : 1
        }, 150);

        contentWrapper.show().css({
            'min-height' : contentWrapper.height(),
        });

        var oldAssetView = assetView;
        assetView = asset.refreshView(assetView);
        if (assetView !== oldAssetView) {
            contentWrapper.empty().append(assetView.contentBox);
            if (oldAssetView !== undefined) oldAssetView.remove();
        }
        assetView.display(asset);

        var displayHeight = asset.getHeightForWidth(contentWrapper.innerWidth());
        if (displayHeight > contentWrapper.height()) {
            /* Grow contentWrapper if necessary */
            contentWrapper.stop(true, false);
            contentWrapper.animate({
                'height' : displayHeight
            }, {
                'duration' : 150,
                'complete' : function() {
                    changedLayout();
                }
            });
        }
    };

    var showCaptionForAsset = function(asset) {
        captionBox.empty();

        var caption = asset.data['caption'];
        var extraHtml = asset.data['extraHtml'];

        if (caption) {
            $('<p>')
                .addClass('caption-main')
                .text(caption)
                .appendTo(captionBox);
        }

        if (extraHtml) {
            $('<p>')
                .addClass('caption-extra')
                .text(extraHtml)
                .appendTo(captionBox);
        }

        captionBox.stop(true, false);
        captionBox.css({
            'opacity' : 1,
            'max-width' : asset.fullDefault.width
        });
    };

    var stopLoadingTimeoutId = undefined;
    var stopLoadingTimeout = function() {
        container.removeClass('loading');
    };

    var onAssetLoading = function(asset, isTransitioning) {
        container.addClass('loading');
        asset.thumbnail.addClass('loading');
        window.clearTimeout(stopLoadingTimeoutId);
        stopLoadingTimeoutId = window.setTimeout(stopLoadingTimeout, 3000);

        if (isTransitioning) {
            captionBox.stop(true, false);
            captionBox.animate({
                'opacity' : 0
            }, 150);
        } else {
            showCaptionForAsset(asset);
        }
    };

    var onAssetLoaded = function(asset) {
        container.removeClass('loading');
        asset.thumbnail.removeClass('loading');

        var displayHeight = asset.getHeightForWidth(contentWrapper.innerWidth());
        contentWrapper.stop(true, false).animate({
            'min-height' : 0,
            'height' : displayHeight
        }, {
            'duration' : 150,
            'complete' : function() {
                contentWrapper.css('height', 'auto');
                changedLayout();
            }
        });

        showCaptionForAsset(asset);

        window.clearTimeout(stopLoadingTimeoutId);
    };

    var onAssetSelectedCb = function(asset) {
        if (asset) {
            showAsset(asset);
        } else {
            hide();
        }
    };

    var init = function() {
        assetSelectedCbs.push(onAssetSelectedCb);
        assetLoadingCbs.push(onAssetLoading);
        assetLoadedCbs.push(onAssetLoaded);

        contentWrapper.css({'cursor' : 'pointer' }).on('click', function(event) {
            selectNextAsset();
        });
    };

    init();
}


function Filmstrip(container) {
    var filmstrip = this;

    container = $(container);

    var synopsisBox = ('.synopsis', container);
    var overflow = $('.overflow', container);
    var leftOverflow = $('.overflow.left', container);
    var rightOverflow = $('.overflow.right', container);
    var pager = $('.pager', container);

    var thumbnailsBox = $('.thumbnails', container);

    var thumbnails = [];
    var thumbnailSize = undefined;
    var pagesTotal = 1;
    var pageSize = 0;
    var currentPage = 0;

    var pagerIsHiding = false;
    var updatePages = function(initial) {
        initial = initial || false;

        if (thumbnailSize) {
            pageSize = Math.floor(container.width() / thumbnailSize);
            pagesTotal = Math.ceil(thumbnails.length / pageSize);
        } else {
            pageSize = 0;
            pagesTotal = 0;
        }

        var updateText = function() {
            $('.total', pager).text('/'+pagesTotal);
            pagerIsHiding = false;
        }

        if (initial) {
            updateText();
            if (pagesTotal <= 1) {
                pager.css('opacity', 0);
            } else {
                pager.show('opacity', 1);
            }
        } else {
            if (pagesTotal <= 1) {
                pagerIsHiding = true;
                pager.animate({'opacity' : 0}, 150, 'linear', updateText);
            } else {
                pagerIsHiding = false;
                updateText();
                pager.animate({'opacity' : 1}, 150, 'linear');
            }
        }

        if (pagesTotal.toString().length > 1) {
            /* Pager needs to make extra space for big numbers */
            pager.addClass('bignumber');
        } else {
            pager.removeClass('bignumber');
        }
    };

    var updateLayout = function(newThumbnails, initial) {
        newThumbnails = newThumbnails || false;
        initial = initial || false;

        if (thumbnails.length > 0) {
            container.removeClass('empty');
        } else {
            container.addClass('empty');
        }

        updatePages(initial)
    };

    var _firstLoad = true;
    var fetchAssets = function(assets, size) {
        $.each(thumbnails, function(index, thumbnail) {
            $(thumbnail).detach();
        });
        thumbnails = [];

        thumbnailsBox.empty();

        $.each(assets, function(index, asset) {
            var thumbnail = asset.thumbnail;
            thumbnailsBox.append(thumbnail);
            thumbnails.push(thumbnail);
            asset._filmstripThumbnail = thumbnail;
        });

        updateLayout(true, _firstLoad);
        _firstLoad = false;
    };

    var pageForIndex = function(index) {
        var page = Math.floor(index / pageSize);
        if (page < 0 || isNaN(page)) page = 0;
        if (page >= pagesTotal) page = pagesTotal-1;
        return page;
    };

    var nearestPageForPosition = function(position) {
        var page = Math.round(position / (thumbnailSize*pageSize));
        if (page < 0 || isNaN(page)) page = 0;
        if (page >= pagesTotal) page = pagesTotal-1;
        return page;
    };

    var nearestAdjacentPageForPosition = function(position) {
        var page = nearestPageForPosition(position);
        if (page > currentPage) {
            page = currentPage+1;
        } else if (page < currentPage) {
            page = currentPage-1;
        }
        return page;
    };

    var showFromIndex = function(startIndex, animate) {
        if (pageSize >= visibleAssets.length) {
            startIndex = 0;
            var endIndex = visibleAssets.length;
        } else {
            var endIndex = startIndex + pageSize;
        }

        var startThumbnail = thumbnailForAsset(visibleAssets[startIndex]);
        var left = startThumbnail ? -(startThumbnail.position().left) : 0;
        $(thumbnailsBox).stop(true, false);
        if (animate) {
            $(thumbnailsBox).animate({
                'left' : left
            }, 250);
        } else {
            $(thumbnailsBox).css('left', left);
        }

        currentPage = pageForIndex(startIndex);
        if (pagesTotal >= 0 && ! pagerIsHiding) {
            $('.current', pager).text(currentPage+1);
        }
    };

    var showPage = function(pageNumber, animate) {
        if (pageNumber < 0) pageNumber = 0;
        if (pageNumber >= pagesTotal) pageNumber = pagesTotal-1;
        startIndex = pageNumber * pageSize;
        showFromIndex(startIndex, animate);
    };

    var shiftPage = function(direction) {
        var nextPage = currentPage + direction;
        if (nextPage < 0 || nextPage >= pagesTotal) nextPage = 0;
        showPage(nextPage, true);
    };

    var thumbnailForAsset = function(asset) {
        if (asset) {
            return asset._filmstripThumbnail;
        } else {
            return undefined;
        }
    };

    var onFilterSelectedCb = function(filter, lastFilter, data) {
        fetchAssets(visibleAssets, 80);
        var changed = (filter != lastFilter);
        var animate = ! (changed || _firstLoad);
        showPage(0, animate);

        if (data['showAsset'] == true) {
            selectAsset(visibleAssets[0]);
        } else if (data['showAsset'] == false) {
            selectAsset(undefined);
        }
    };

    var onAssetSelectedCb = function(asset) {
        if (asset !== undefined && visibleFilter !== undefined) {
            assetPage = pageForIndex(visibleFilter.assetNumber(asset));
            if (currentPage != assetPage) {
                showPage(assetPage, true);
            }
        }
    };

    var thumbnailsStartPosition = undefined;
    var touchMoved = false;
    var touchStart = {x : 0, y : 0};
    var touchStartTime = 0;

    var onContainerTouchStart = function(event) {
        thumbnailsStartPosition = thumbnailsBox.position();

        thumbnailsBox.stop(true, false);

        touchMoved = false;
        touchStart.x = event.originalEvent.touches[0].pageX;
        touchStart.y = event.originalEvent.touches[0].pageY;
        touchStartTime = new Date().getTime();
    };

    var onContainerTouchMove = function(event) {
        var offsetX = touchStart.x - event.originalEvent.touches[0].pageX;
        var offsetY = touchStart.y - event.originalEvent.touches[0].pageY;

        if (Math.abs(offsetX) > Math.abs(offsetY)) {
            touchMoved = true;
            event.preventDefault();
        }

        thumbnailsBox.css({
            'left' : thumbnailsStartPosition.left - offsetX
        });
        var currentPage = nearestPageForPosition(-thumbnailsBox.position().left);
        $('.current', pager).text(currentPage+1);
    };

    var onContainerTouchEnd = function(event) {
        /* Snap to the nearest page (bounceback) */

        var now = new Date().getTime();

        /* Calculate average momentum */
        var touchDuration = now - touchStartTime;
        var touchDistance = thumbnailsBox.position().left - thumbnailsStartPosition.left;
        var touchVelocity = Math.round(touchDistance / touchDuration);
        /* Only use momentum if the touch has covered a significant distance (filters out accidental touches) */
        var slippiness = 800;
        if (Math.abs(touchDistance) < 65) slippiness = 0;
        var touchMomentum = slippiness * touchVelocity;

        var left = -(thumbnailsBox.position().left + touchMomentum);
        var snapPage = nearestAdjacentPageForPosition(left);
        showPage(snapPage, true);

        touchMoved = false;
        touchStart.x = 0;
        touchStart.y = 0;
    };

    var onContainerTouchCancel = function(event) {
        onContainerTouchEnd(event);
    };

    this.rewind = function(animate) {
        showPage(0, animate);
    };

    this.isAtStart = function() {
        return currentPage == 0;
    };

    var init = function() {
        filterSelectedCbs.push(onFilterSelectedCb);
        assetSelectedCbs.push(onAssetSelectedCb);

        $(window).on('resize', function(event) {
            updateLayout();
            showPage(currentPage, true);
        });

        container.on('touchstart', onContainerTouchStart);
        container.on('touchmove', onContainerTouchMove);
        container.on('touchend', onContainerTouchEnd);
        container.on('touchcancel', onContainerTouchCancel);

        thumbnailsBox.on('click', 'a.asset', function(event) {
            event.preventDefault();
            var asset = $(this).data('asset');
            toggleAsset(asset);
        });

        leftOverflow.on('click', function(event) {
            event.preventDefault();
            shiftPage(-1);
        });

        rightOverflow.on('click', function(event) {
            event.preventDefault();
            shiftPage(1);
        });
    };

    init();
}


function Filter(allAssets, button) {
    var filter = this;

    button = $(button);

    this.name = undefined;
    this.url = undefined;
    this.categories = [];
    this.autoOpen = false;
    this.isDefaultFilter = undefined;

    this.assetNumber = function(asset) {
        return $.inArray(selectedAsset, this.assets);
    };

    this.getNextAsset = function(direction) {
        assetNumber = $.inArray(selectedAsset, this.assets);
        assetNumber += direction;
        if (assetNumber < 0) {
            return undefined;
        } else if (assetNumber >= this.assets.length) {
            return undefined;
        } else {
            return this.assets[assetNumber];
        }
    };

    this.containsAsset = function(asset) {
        return $.inArray(asset, this.assets) >= 0;
    };

    var modWithNegative = function(a, b) {
        return ((a%b)+b)%b;
    };

    var arrayContainsAny = function(a, b) {
        if (a.length == 0) return true;

        for (i = 0; i < a.length; i++) {
            var aItem = a[i];
            if ($.inArray(aItem, b) >= 0) {
                return true;
            }
        }
        return false;
    };

    var onFilterSelectedCb = function(newFilter) {
        if (newFilter == filter) {
            button.addClass('current');
        } else {
            button.removeClass('current');
        }
    };

    var init = function() {
        filterSelectedCbs.push(onFilterSelectedCb);

        var autoOpen = $(button).data('filter-auto-open') !== undefined;
        var isDefaultFilter = $(button).data('filter-default') !== undefined;

        var url = $(button).attr('href');

        var mainStr = filterNameFromUrl(url);
        if (mainStr && mainStr in galleries) {
            filter.galleryName = mainStr;
            filter.gallery = galleries[filter.galleryName];
            filter.categories.push(filter.galleryName);
        }

        filter.autoOpen = autoOpen;
        filter.isDefaultFilter = isDefaultFilter;
        filter.url = url;
        if (mainStr) {
            filter.name = mainStr;
        } else if (mainStr && isDefaultFilter) {
            filter.name = '*';
        }

        $(button).on('click', function(event) {
            event.preventDefault();
            if (filter == selectedFilter && selectedAsset !== undefined) {
                // allow collapsing the filter by clicking a second time
                selectAsset(undefined);
            } else if (filter == selectedFilter) {
                selectAsset(visibleAssets[0]);
            } else {
                var History = window.History;
                goToFilter(filter, {showAsset: true});
            }
            scrollToMedia(false);
        });

        filter.assets = [];
        $.each(allAssets, function(index, asset) {
            if (arrayContainsAny(filter.categories, asset.data['categories'])) {
                filter.assets.push(asset);
            }
        });
    };

    init();
}


function Portfolio(container) {
    var portfolio = this;

    container = $(container);

    var synopsisBox = $('.synopsis', container);
    var filmstripBox = $('.filmstrip', container);
    var viewerBox = $('.viewer', container);

    var synopsisContent = $('<p>').appendTo(synopsisBox);

    var onFilterSelectedCb = function(filter) {
        if (filter && filter.gallery && 'synopsis' in filter.gallery) {
            synopsisBox.text(filter.gallery.synopsis).show();
            /*synopsisBox.animate({
                'opacity' : 'show',
                'margin' : 'show',
                'padding-top' : 'show',
                'padding-bottom' : 'show',
                'height' : 'show'
            }, 150);*/
        } else {
            synopsisBox.empty().hide();
            /*synopsisBox.animate({
                'opacity' : 'hide',
                'margin' : 'hide',
                'padding-top' : 'hide',
                'padding-bottom' : 'hide',
                'height' : 'hide'
            }, 150);*/
        }
    };

    this.navUp = function() {
        if (selectedAsset === undefined) {
            if (this.filmstrip.isAtStart()) {
                goToFilter(undefined, {showAsset: false});
            } else {
                this.filmstrip.rewind(true);
            }
        } else {
            selectAsset(undefined);
        }
        scrollToMedia(true);
    };

    var init = function() {
        portfolio.filmstrip = new Filmstrip(filmstripBox);
        portfolio.viewerBox = new ViewerBox(viewerBox);

        filterSelectedCbs.push(onFilterSelectedCb);
    };

    init();
}


var _DEFAULT_SELECT_FILTER_DATA = {
    showAsset: false
}
var filterSelectedCbs = [];
var selectedFilter = undefined;
var visibleFilter = undefined;
var visibleAssets = [];
var selectFilter = function(filter, data) {
    data = $.extend({}, _DEFAULT_SELECT_FILTER_DATA, data);

    if (!filter) {
        data['showAsset'] = false;
    } else if (!filter.autoOpen) {
        data['showAsset'] = false;
    }

    var lastFilter = selectedFilter;
    selectedFilter = filter;
    visibleFilter = filter || defaultFilter;
    visibleAssets = (visibleFilter) ? visibleFilter.assets : [];

    $.each(filterSelectedCbs, function(index, cb) {
        cb(visibleFilter, lastFilter, data);
    });

    if (lastFilter !== undefined && lastFilter != visibleFilter) {
        var filterName = (visibleFilter) ? visibleFilter.name : '/';
        trackEvent(['_trackEvent', 'Portfolio', 'Filter', filterName]);
    }
};


var _DEFAULT_SELECT_ASSET_DATA = {}
var assetSelectedCbs = [];
var selectedAsset = undefined;
var selectAsset = function(asset, data) {
    data = $.extend({}, _DEFAULT_SELECT_ASSET_DATA, data);

    var lastAsset = selectedAsset;
    selectedAsset = asset;

    $.each(assetSelectedCbs, function(index, cb) {
        cb(asset, lastAsset, data);
    });

    if (asset) {
        trackEvent(['_trackEvent', 'Portfolio', 'Selected', asset.name]);
    } else {
        trackEvent(['_trackEvent', 'Portfolio', 'Deselected']);
    }
};


var goToFilter = function(filter, data) {
    if (filter) {
        pushHistory(data, SITE_TITLE, filter.url);
    } else {
        pushHistory(data, SITE_TITLE, SITE_BASE);
    }
};


var toggleAsset = function(asset) {
    if (asset != selectedAsset) {
        selectAsset(asset);
    } else {
        selectAsset(undefined);
    }
    scrollToMedia(false);
};


var selectNextAsset = function(direction) {
    direction = direction || 1;
    if (visibleFilter) {
        var nextAsset = visibleFilter.getNextAsset(direction);
        selectAsset(nextAsset);
        if (!nextAsset) {
            selectFilter(visibleFilter, {showAsset: false});
        }
        scrollToMedia(false);
    }
};


var assetLoadingCbs = [];
var loadingAsset = function(asset, isTransitioning, assetView) {
    if (!asset) return;
    $.each(assetLoadingCbs, function(index, cb) {
        cb(asset, isTransitioning, assetView);
    });
};


var assetLoadedCbs = [];
var loadedAsset = function(asset, assetView) {
    if (!asset) return;
    $.each(assetLoadedCbs, function(index, cb) {
        cb(asset, assetView);
    });
};


var layoutChangedCbs = [];
var changedLayout = function() {
    $.each(layoutChangedCbs, function(index, cb) {
        cb();
    });
};


var filterNameFromUrl = function(url) {
    if (url) {
        var urlParts = url.split('/');
        var pathName = undefined;
        while (urlParts.length > 0 && !pathName) {
            pathName = urlParts.pop();
        }
        return pathName;
    } else {
        return undefined;
    }
};


var filterForPath = function(url) {
    var filterName = filterNameFromUrl(url);
    return filters[filterName];
};


var loadGallery = function(galleryName, galleryData) {
    galleries[galleryName] = galleryData
    if (galleryData['abstractId'] !== undefined) {
        var abstractElem = $('#'+galleryData['abstractId']);
        if (abstractElem.length > 0) {
            galleryData['abstractElem'] = abstractElem.detach();
        }
    }
};


var loadMedia = function(mediaIndex, mediaData) {
    mediaData = $.extend({}, DEFAULT_ASSET_DATA, mediaData);
    galleryName = mediaData['gallery'];
    var asset = new Asset(mediaIndex, mediaData, galleryName);
    assets.push(asset);
}


var scrollToMedia = function(force) {
    var focusTop = 0;

    if (selectedAsset && selectedFilter) {
        var synopsisBox = $('.synopsis');
        var filmstripBox = $('.filmstrip');
        if (synopsisBox.length > 0) {
            focusTop = synopsisBox.offset().top - 4;
        } else if (filmstripBox.length > 0) {
            focusTop = filmstripBox.offset().top - 4;
        }
    } else if (selectedFilter) {
        var filtersBox = $('.filters');
        if (filtersBox.length > 0) {
            focusTop = filtersBox.offset().top;
        }
    }

    if (SMC_AUTOSCROLL === true || force === true) {
        $('html, body').stop(true, false).animate({
            'scrollTop' : focusTop
        }, 150);
    }
}


$(document).ready(function () {
    $.each(SMC_GALLERIES, loadGallery);
    $.each(SMC_MEDIA, loadMedia);

    var portfolioBox = $('.portfolio');
    var portfolio = new Portfolio(portfolioBox);
    var filtersBox = $('.filters', portfolioBox);

    $('.filter', filtersBox).each(function(index, filterButton) {
        var filter = new Filter(assets, filterButton);
        filters[filter.name] = filter;

        if (filter.isDefaultFilter) {
            defaultFilter = filter;
        }
    });

    filtersBox.on('click', function(event) {
        if ($(event.target).is(filtersBox)) {
            selectAsset(undefined);
        }
    });

    $('.synopsis').on('click', function(event) {
        selectAsset(undefined);
        scrollToMedia(false);
    });

    $('.action-return').on('click', function(event) {
        goToFilter(undefined);
        scrollToMedia(false);
        event.preventDefault();
    });

    $('.nav-menu').on('change', function(event) {
        event.preventDefault();
        var destFilter = filters[$(this).val()];
        goToFilter(destFilter, {showAsset: true});
        scrollToMedia(false);
    });

    $('a.gallery-link').on('click', function(event) {
        event.preventDefault();
        var destUrl = $(this).attr('href');
        var destFilter = filterForPath(destUrl);
        goToFilter(destFilter, {showAsset: true});
        scrollToMedia(false);
    });

    $('a.back-to-top-link').on('click', function(event) {
        event.preventDefault();

        $('html, body').stop(true, false).animate({
            'scrollTop' : $('.filters').offset().top
        }, 150);
    });

    $(document).on('keydown', function(event) {
        if (event.which == 37) {
            // left arrow
            selectNextAsset(-1);
        } else if (event.which == 39) {
            // right arrow
            selectNextAsset(1);
        } else if (event.which == 27) {
            // escape key
            portfolio.navUp();
        }
    });
});


$(document).ready(function() {
    assetSelectedCbs.push(function(asset, lastAsset, data) {
        if (asset == undefined) {
            $('body').removeClass('showing-asset');
        } else {
            $('body').addClass('showing-asset');
        }
    });

    filterSelectedCbs.push(function(filter, lastFilter, data) {
        var galleryContentWrapper = $('.gallery-content');
        var galleryContent = $('.content-inner', galleryContentWrapper);

        if (filter === undefined) {
            $('body').removeClass('showing-gallery');
            galleryContentWrapper.hide();
            galleryContent.children().detach();
        } else {
            $('body').addClass('showing-gallery');
            galleryContent.children().detach();

            if (filter.gallery && filter.gallery['abstractElem']) {
                galleryContent.append(filter.gallery['abstractElem']);
                galleryContentWrapper.show();
            } else {
                galleryContentWrapper.hide();
            }
        }
    });
});

$(document).ready(function () {
    $(window).on('popstate', onHistoryChange);
    onHistoryChange();
});

})();

// Global setup

var _YOUTUBE_IS_READY = false;
var _YOUTUBE_READY_CALLBACKS = [];

// Load YouTube IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function onYouTubeIframeAPIReady() {
    _YOUTUBE_IS_READY = true;
    $.each(_YOUTUBE_READY_CALLBACKS, function(index, callback) {
        callback();
    });
}

function doWhenYouTubeIsReady(callback) {
    if (_YOUTUBE_IS_READY) {
        callback();
    } else {
        _YOUTUBE_READY_CALLBACKS.push(callback);
    }
}
