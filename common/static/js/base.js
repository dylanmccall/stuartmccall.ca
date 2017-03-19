(function NorthLight () {

/* Front-end JavaScript for stuartmccall.ca / northlightimages.com
 *
 * Copyright (C) Dylan McCall <www.dylanmccall.com>
 */

$ = jQuery;

var galleries = {};
var filters = {};
var assets = [];
var assetsByName = {};

var defaultFilter = undefined;

var SITE_TITLE = document.title;
var SITE_BASE = '/';

var DEFAULT_ASSET_DATA = {
    'type' : 'picture'
}


var trackEvent = function(data) {
    if (typeof _gaq !== 'undefined') {
        _gaq.push(data);
    } else {
        console.log("Tracking event", data);
    }
}


function Asset(name, data, galleryName) {
    var asset = this;

    var defaultCategories = [];

    if (galleryName) defaultCategories.push(galleryName);
    
    this.name = name
    this.data = $.extend({ 'categories' : defaultCategories}, data);
    this.galleryName = galleryName;

    var THUMBNAIL_CLASSES = {
        'picture' : 'picture',
        'video-youtube' : 'video'
    }
    
    var thumbnailForSize = function(size) {
        var thumbnailName = asset.data.thumbnail || asset.name;
        var thumbnailClass = THUMBNAIL_CLASSES[data.type];

        var thumbnail = $('<a>').attr({
            'role' : 'img button',
            'class' : 'asset',
            'href' : asset.data['full'].src,
            'title' : asset.data['title']
        }).addClass(thumbnailClass).data('asset', asset);
        $('<div>').attr({
            'class' : 'overlay'
        }).appendTo(thumbnail);
        $('<img>').attr({
            'src' : asset.data['thumb'].src,
            'width' : asset.data['thumb'].width,
            'height' : asset.data['thumb'].height,
            'alt' : '',
            'aria-hidden' : 'true'
        }).appendTo(thumbnail);

        return thumbnail;
    }
    
    var onAssetSelectedCb = function(selectedAsset) {
        if (selectedAsset == asset) {
            asset.thumbnail.addClass('current');
        } else {
            asset.thumbnail.removeClass('current');
            asset.thumbnail.removeClass('loading');
        }
    }

    this.getHeightForWidth = function(maxWidth) {
        var ratio = this.data['full'].height / this.data['full'].width;
        var displayWidth = Math.min(this.data['full'].width, maxWidth);
        var displayHeight = Math.min(displayWidth * ratio, this.data['full'].height);
        return displayHeight;
    }

    this.refreshView = function(existingView) {
        if (existingView !== undefined && existingView.fitsAsset(this)) {
            return existingView;
        } else if (this.data['type'] === 'picture') {
            return new PictureAssetView();
        } else if (this.data['type'] === 'video-youtube') {
            return new VideoAssetView();
        }
    }
    
    var init = function() {
        assetSelectedCbs.push(onAssetSelectedCb);
        
        asset.thumbnail = thumbnailForSize(80);
        asset.thumbnail.on('click', function(event) {
            event.preventDefault();
        });
    }
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
    }

    this.getHeightForAsset = function(asset, container) {
        return asset.getHeightForWidth(container.innerWidth());
    }

    this.display = function(asset) {
        if (content === undefined) {
            content = this.createContent(asset);
        } else {
            content = this.updateContent(asset, content);
        }
    }

    this.remove = function() {
        this.contentBox.empty();
        content = undefined;
    }
}


function PictureAssetView() {
    var pictureAssetView = this;

    this.contentBox.addClass('asset-picture');

    this.fitsAsset = function(asset) {
        return asset.data['type'] === 'picture';
    }

    this.createContent = function(asset) {
        var content = $('<img>')
            .on('load', onImgLoaded)
            .appendTo(this.contentBox);

        updateImgWithAsset(content, asset)
        loadingAsset(asset, true, pictureAssetView);

        return content;
    }

    this.updateContent = function(asset, content) {
        if (content.attr('src') === asset.data['full'].src) {
            loadedAsset(asset, pictureAssetView);
        } else {
            // I wish I could set width and height here, but it causes the existing image to stretch
            loadingAsset(asset, false, pictureAssetView);
            updateImgWithAsset(content, asset);
        }

        return content;
    }

    var updateImgWithAsset = function(img, asset) {
        img.attr({
            'src' : asset.data['full'].src,
            'width' : asset.data['full'].width,
            'height' : asset.data['full'].height,
            'alt' : asset.name
        });
        img.data('asset', asset);
    }

    var onImgLoaded = function(event) {
        asset = $(this).data('asset');
        if (asset) loadedAsset(asset, pictureAssetView);
    }
}
PictureAssetView.prototype = new AssetView();


function VideoAssetView() {
    var videoAssetView = this;

    this.contentBox.addClass('asset-video-youtube');

    var player = undefined;
    var playerReady = false;
    var playerVideo = undefined;

    var currentAsset = undefined;

    this.fitsAsset = function(asset) {
        return asset.data['type'] === 'video-youtube';
    }

    this.createContent = function(asset) {
        var playerElem = $('<div>')
            .addClass('player')
            .appendTo(this.contentBox)
            .css({'visibility' : 'hidden'});

        player = new YT.Player(playerElem[0], {
            'width': asset.data['full'].width,
            'height': asset.data['full'].height,
            'videoId': asset.data['youtube-video-id'],
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

        //loadingAsset(asset, false, videoAssetView);
        loadedAsset(selectedAsset, videoAssetView);
        return playerElem;
    }

    this.updateContent = function(asset, content) {
        this.videoSelected(asset);
        loadedAsset(asset, videoAssetView);
        return content;
    }

    var onPlayerReady = function() {
        playerReady = true;
        if (selectedAsset) videoAssetView.videoSelected(selectedAsset);
        loadedAsset(selectedAsset, videoAssetView);
        $(player.getIframe()).css({'visibility' : 'visible'})
    }

    this.videoSelected = function(asset) {
        if (!playerReady) return;
        
        var previousVideo = playerVideo;
        var previousState = player.getPlayerState();
        
        if (previousVideo == asset) {
            player.playVideo();
        } else {
            var wasPlaying = (previousState == 0 || previousState == 1 || previousState == 3);
            if (wasPlaying) {
                player.loadVideoById(asset.data['youtube-video-id'], 0, 'large');
            } else  {
                player.cueVideoById(asset.data['youtube-video-id'], 0, 'large');
            }
            player.setSize(asset.data['full'].width, asset.data['full'].height);
        }
        
        playerVideo = asset;
    }
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
    }
    
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
    }

    var showCaptionForAsset = function(asset) {
        captionBox.empty();

        $('<p>')
            .addClass('caption-main')
            .html(asset.data['caption_html'])
            .appendTo(captionBox);

        var printDim = asset.data['print-dimensions'];
        if (printDim !== undefined) {
            $('<p>')
                .addClass('caption-extra')
                .text(printDim[0] + "\u2033 \u00D7 " + printDim[1] + "\u2033")
                .appendTo(captionBox);
        }

        captionBox.stop(true, false);
        captionBox.css({
            'opacity' : 1,
            'max-width' : asset.data['full'].width
        });
    }

    var stopLoadingTimeoutId = undefined;
    var stopLoadingTimeout = function() {
        container.removeClass('loading');
    }

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
    }
    
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
    }
    
    var onAssetSelectedCb = function(asset) {
        if (asset) {
            showAsset(asset);
        } else {
            hide();
        }
    }
    
    var init = function() {
        assetSelectedCbs.push(onAssetSelectedCb);
        assetLoadingCbs.push(onAssetLoading);
        assetLoadedCbs.push(onAssetLoaded);

        contentWrapper.css({'cursor' : 'pointer' }).on('click', function(event) {
            selectNextAsset();
        });
    }
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
    }
    
    var updateLayout = function(newThumbnails, initial) {
        newThumbnails = newThumbnails || false;
        initial = initial || false;
        
        function layoutForSize(size) {
            $.each(thumbnails, function(index, thumbnail) {
                $(thumbnail).css({
                    'position' : 'absolute',
                    'left' : index * size
                });
            });
        }
        
        if (thumbnails.length > 0) {
            container.removeClass('empty');
            var newSize = $(thumbnails[0]).width();
            if (newThumbnails || newSize != thumbnailSize) {
                thumbnailSize = newSize;
                layoutForSize(newSize);
            }
        } else {
            container.addClass('empty');
        }
        
        updatePages(initial)
    }
    
    var _firstLoad = true;
    var loadAssets = function(assets, size) {
        $.each(thumbnails, function(index, thumbnail) {
            $(thumbnail).detach();
        });
        thumbnails = [];

        $.each(assets, function(index, asset) {
            var thumbnail = asset.thumbnail; // TODO: Generate a thumbnail inteligently
            thumbnailsBox.append(thumbnail);
            thumbnails.push(thumbnail);
            asset._filmstripThumbnail = thumbnail;
        });
        
        updateLayout(true, _firstLoad);
        _firstLoad = false;
    }
    
    var pageForIndex = function(index) {
        var page = Math.floor(index / pageSize);
        if (page < 0 || isNaN(page)) page = 0;
        if (page >= pagesTotal) page = pagesTotal-1;
        return page;
    }
    
    var nearestPageForPosition = function(position) {
        var page = Math.round(position / (thumbnailSize*pageSize));
        if (page < 0 || isNaN(page)) page = 0;
        if (page >= pagesTotal) page = pagesTotal-1;
        return page;
    }
    
    var nearestAdjacentPageForPosition = function(position) {
        var page = nearestPageForPosition(position);
        if (page > currentPage) {
            page = currentPage+1;
        } else if (page < currentPage) {
            page = currentPage-1;
        }
        return page;
    }
    
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
    }
    
    var showPage = function(pageNumber, animate) {
        if (pageNumber < 0) pageNumber = 0;
        if (pageNumber >= pagesTotal) pageNumber = pagesTotal-1;
        startIndex = pageNumber * pageSize;
        showFromIndex(startIndex, animate);
    }
    
    var shiftPage = function(direction) {
        var nextPage = currentPage + direction;
        if (nextPage < 0 || nextPage >= pagesTotal) nextPage = 0;
        showPage(nextPage, true);
    }
    
    var thumbnailForAsset = function(asset) {
        if (asset) {
            return asset._filmstripThumbnail;
        } else {
            return undefined;
        }
    }
    
    var onFilterSelectedCb = function(filter, lastFilter, data) {
        loadAssets(visibleAssets, 80);
        var changed = (filter != lastFilter);
        var animate = ! (changed || _firstLoad);
        showPage(0, animate);

        if (data['showAsset'] == true) {
            if (!filter.gallery['abstract-elem']) {
                selectAsset(visibleAssets[0]);
            } else {
                selectAsset(undefined);
            }
        } else if (data['showAsset'] == false) {
            selectAsset(undefined);
        }
    }
    
    var onAssetSelectedCb = function(asset) {
        if (asset !== undefined && visibleFilter !== undefined) {
            assetPage = pageForIndex(visibleFilter.assetNumber(asset));
            if (currentPage != assetPage) {
                showPage(assetPage, true);
            }
        } else {
            //showPage(0, true);
        }
    }
    
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
    }
    
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
    }
    
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
    }
    
    var onContainerTouchCancel = function(event) {
        onContainerTouchEnd(event);
    }

    this.rewind = function(animate) {
        showPage(0, animate);
    }

    this.isAtStart = function() {
        return currentPage == 0;
    }
    
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
    }
    init();
}


function Filter(allAssets, button) {
    var filter = this;
    
    button = $(button);

    this.name = undefined;
    
    this.assetNumber = function(asset) {
        return $.inArray(selectedAsset, this.assets);
    }
    
    this.getNextAsset = function(direction) {
        assetNumber = $.inArray(selectedAsset, this.assets);
        if (assetNumber < 0) {
            assetNumber = 0;
        } else {
            assetNumber = modWithNegative(assetNumber+direction, this.assets.length);
        }
        return this.assets[assetNumber];
    }
    
    this.containsAsset = function(asset) {
        return $.inArray(asset, this.assets) >= 0;
    }
    
    var modWithNegative = function(a, b) {
        return ((a%b)+b)%b;
    }
    
    var arrayContainsAny = function(a, b) {
        if (a.length == 0) return true;
        
        for (i = 0; i < a.length; i++) {
            var aItem = a[i];
            if ($.inArray(aItem, b) >= 0) {
                return true;
            }
        }
        return false;
    }
    
    var onFilterSelectedCb = function(newFilter) {
        if (newFilter == filter) {
            button.addClass('current');
        } else {
            button.removeClass('current');
        }
    }
    
    var init = function() {
        filterSelectedCbs.push(onFilterSelectedCb);
        
        var categoriesStr = $(button).data('filter-category');
        if (categoriesStr) {
            filter.categories = categoriesStr.split(' ');
        } else {
            filter.categories = [];
        }

        var mainStr = filterNameFromUrl($(button).attr('href'));
        if (mainStr && mainStr in galleries) {
            filter.galleryName = mainStr;
            filter.gallery = galleries[filter.galleryName];
            filter.categories.push(filter.galleryName);
        }

        filter.name = mainStr || categoriesStr || '[All]';
        
        $(button).on('click', function(event) {
            event.preventDefault();
            if (filter == selectedFilter && selectedAsset !== undefined) {
                // allow collapsing the filter by clicking a second time
                selectAsset(undefined);
            } else if (filter == selectedFilter) {
                selectAsset(visibleAssets[0]);
            } else {
                var History = window.History;
                goToFilter(filter);
            }
        });
        
        filter.assets = [];
        $.each(allAssets, function(index, asset) {
            if (arrayContainsAny(filter.categories, asset.data['categories'])) {
                filter.assets.push(asset);
            }
        });
    }
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
    }

    this.navUp = function() {
        if (selectedAsset === undefined) {
            if (this.filmstrip.isAtStart()) {
                goToFilter(undefined);
            } else {
                this.filmstrip.rewind(true);
                goToFilter(selectedFilter);
            }
        } else {
            selectAsset(undefined);
            goToFilter(selectedFilter);
        }
    }

    var init = function() {
        portfolio.filmstrip = new Filmstrip(filmstripBox);
        portfolio.viewerBox = new ViewerBox(viewerBox);

        filterSelectedCbs.push(onFilterSelectedCb);
    }
    init();
}


var _DEFAULT_SELECT_FILTER_DATA = {
    'showAsset' : false
}
var filterSelectedCbs = [];
var selectedFilter = undefined;
var visibleFilter = undefined;
var visibleAssets = [];
var selectFilter = function(filter, data) {
    if (filter === undefined) {
        data = $.extend({'showAsset' : false}, data);
    }
    data = $.extend({}, _DEFAULT_SELECT_FILTER_DATA, data);
    
    var lastFilter = selectedFilter;
    selectedFilter = filter;
    visibleFilter = filter || defaultFilter;
    visibleAssets = (visibleFilter) ? visibleFilter.assets : [];
    
    $.each(filterSelectedCbs, function(index, cb) {
        cb(filter, lastFilter, data);
    });
    
    if (lastFilter !== undefined && lastFilter != visibleFilter) {
        var filterName = (visibleFilter) ? visibleFilter.name : '/';
        trackEvent(['_trackEvent', 'Portfolio', 'Filter', filterName]);
    }
}


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
}


var goToFilter = function(filter) {
    filtersTop = filter ? $('.filters').offset().top : 0;
    $('html, body').stop(true, false).animate({
        'scrollTop' : filtersTop
    }, 150);
    if (filter) {
        History.pushState(undefined, SITE_TITLE, SITE_BASE+filter.name);
    } else {
        History.pushState(undefined, SITE_TITLE, SITE_BASE);
    }
}


var toggleAsset = function(asset) {
    if (asset != selectedAsset) {
        // TODO: Can we rely on the StateChange handler being called before selectAsset?
        goToFilter(visibleFilter);
        selectAsset(asset);
    } else {
        selectAsset(undefined);
    }
}


var selectNextAsset = function(direction) {
    direction = direction || 1;
    if (selectedFilter) {
        var nextAsset = selectedFilter.getNextAsset(direction);
        selectAsset(nextAsset);
    }
}


var assetLoadingCbs = [];
var loadingAsset = function(asset, isTransitioning, assetView) {
    if (!asset) return;
    $.each(assetLoadingCbs, function(index, cb) {
        cb(asset, isTransitioning, assetView);
    });
}


var assetLoadedCbs = [];
var loadedAsset = function(asset, assetView) {
    if (!asset) return;
    $.each(assetLoadedCbs, function(index, cb) {
        cb(asset, assetView);
    });
}


var layoutChangedCbs = [];
var changedLayout = function() {
    $.each(layoutChangedCbs, function(index, cb) {
        cb();
    });
}


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
}


var filterForPath = function(url) {
    var filterName = filterNameFromUrl(url);
    return filters[filterName];
}


var loadAsset = function(assetName, assetData, galleryName) {
    var asset = new Asset(assetName, assetData, galleryName);
    assets.push(asset);
    assetsByName[assetName] = asset;
}


var loadGallery = function(galleryName, galleryData) {
    galleries[galleryName] = galleryData
    galleryAssets = galleryData['media'];
    if (galleryData['abstract-id'] !== undefined) {
        galleryData['abstract-elem'] = $('#'+galleryData['abstract-id']).detach();
    }
    $.each(galleryAssets, function(assetName, assetData) {
        assetData = $.extend({}, DEFAULT_ASSET_DATA, assetData);
        loadAsset(assetName, assetData, galleryName);
    });
}


$(document).ready(function () {
    $.each(SMC_GALLERIES, loadGallery);

    var portfolioBox = $('.portfolio');
    var portfolio = new Portfolio(portfolioBox);
    var filtersBox = $('.filters', portfolioBox);

    $('.filter', filtersBox).each(function(index, filterButton) {
        var filter = new Filter(assets, filterButton);
        filters[filter.name] = filter;

        if ($(this).data('default-filter') !== undefined) {
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
    });

    $('.action-return').on('click', function(event) {
        goToFilter(undefined);
        event.preventDefault();
    });

    $('.nav-menu').on('change', function(event) {
        event.preventDefault();
        var destFilter = filters[$(this).val()];
        goToFilter(destFilter);
    });

    $('a.gallery-link').on('click', function(event) {
        event.preventDefault();
        var destUrl = $(this).attr('href');
        var destFilter = filterForPath(destUrl);
        goToFilter(destFilter);
    });

    $('a.back-to-top-link').on('click', function(event) {
        event.preventDefault();

        $('html, body').stop(true, false).animate({
            'scrollTop' : $('.filters').offset().top
        }, 150);

        // if (visibleAssets && selectedAsset === undefined) {
        //  selectAsset(visibleAssets[0]);
        // }
    });
    
    $(document).on('keydown', function(event) {
        if (event.which == 37 && selectedFilter !== undefined) {
            // left arrow
            selectNextAsset(-1);
        } else if (event.which == 39 && selectedFilter !== undefined) {
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

        // if (asset === undefined) {
        //  var filtersTop = 0;
        // } else {
        //  var filtersTop = filtersBox.offset().top;
        // }
        // $('html, body').stop(true, false).animate({
        //  'scrollTop' : filtersTop
        // }, 150);
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

            if (filter.gallery && filter.gallery['abstract-elem']) {
                galleryContent.append(filter.gallery['abstract-elem']);
                galleryContentWrapper.show();
            } else {
                galleryContentWrapper.hide();
            }
        }
    });
});


// $(document).ready(function () {
//  var updateBlurElems = function() {
//      $('.blur').each(function(id, blur) {
//          var topEdge = $(blur).offset().top;
//          var bottomEdge = topEdge + $(blur).height();

//          var blurMiddleRatio = Number($(blur).data('blur-from')) || 0.5;

//          var scrollHeight = $(window).height();
//          var scrollTop = $(window).scrollTop();
//          var scrollMiddle = scrollTop + (scrollHeight * blurMiddleRatio);
//          var scrollBottom = scrollTop + scrollHeight;

//          // element is considered onscreen if it is within the top 40% of
//          // the viewport, or its bottom edge is visible.
//          var onscreen = false
//              || (scrollTop > topEdge)
//              || (topEdge > scrollTop && topEdge < scrollMiddle)
//              || (bottomEdge < scrollBottom);

//          if (!onscreen) {
//              $(blur).addClass('offscreen');
//          } else {
//              $(blur).removeClass('offscreen');
//          }
//      });
//  }

//  $(window).on('scroll resize', updateBlurElems);
//  filterSelectedCbs.push(updateBlurElems);
//  layoutChangedCbs.push(updateBlurElems);
// });


$(document).ready(function () {
    var History = window.History;
    if (!History.enabled ) {
        // Fall back to hash change events. Automatic?
    }

    var getPath = function(href) {
        var parser = document.createElement("a");
        parser.href = href;
        return parser.pathname;
    };

    History.Adapter.bind(window, 'statechange', function() {
        var State = History.getState();
        // var statePath = getPath(State.cleanUrl);
        var statePath = State.cleanUrl;
        // filter name?
        var stateFilter = filterForPath(statePath);
        selectFilter(stateFilter, State.data);
        if (stateFilter) {
            $('.nav-menu').val(stateFilter.name);
        } else {
            $('.nav-menu').val('');
        }
    });

    History.Adapter.trigger(window, 'statechange');
});


})();
