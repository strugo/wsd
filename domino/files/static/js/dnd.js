function getElementXY(clientX, clientY) {
    var target = document.elementFromPoint(clientX, clientY);

    if (!target || target == document) {
      target = document.body;
    }

    return target;
}

function getElementUnderClientXY(elem, clientX, clientY) {
    var display = elem.style.display || '';
    elem.style.display = 'none';

    var target = getElementXY(clientX, clientY);

    elem.style.display = display;

    return target;
}

function getDivElementXY(clientX, clientY) {
    var target = getElementXY(clientX, clientY);
    while (target != document && target.tagName != 'DIV') {
        target = target.parentNode;
    }
    return target;
}

var DOTS = []
var i = 0;
while (i < 4) {
    var d = document.createElement('div');
    d.style.position = 'absolute';
    DOTS.push(d);
    i++
}

DOTS[0].style.border = '3px solid red';
DOTS[1].style.border = '3px solid green';
DOTS[2].style.border = '3px solid yellow';
DOTS[3].style.border = '3px solid blue';
//DOTS[d].style.left = X+'px';
//DOTS[d].style.top = Y+'px';
//DOTS[d].textContent = X + ' ' + Y;
//document.body.appendChild(DOTS[d]);

var dragManager = new function() {

    var dragChip, avatar, dropTarget, lastDropTarget;
    var downX, downY;
    var lastX, lastY;

    var self = this;

    function onMouseDown(e){
        if (e.which != 1 ) {
            return false;
        }

        dragChip = findDragChip(e);

        if (!dragChip) {
            return;
        }

        downX = lastX = e.pageX;
        downY = lastY = e.pageY;

        return false;
    }

    function onMouseMove(e) {
        if (!dragChip) return;

        if ( !avatar ) {
            if ( Math.abs(e.pageX-downX) < 3 && Math.abs(e.pageY-downY) < 3 ) {
              return;
            }
            avatar = dragChip.onDragStart(downX, downY, e);

            if (!avatar) {
                cleanUp();
                return;
            }
        }

        avatar.onDragMove(e);


        //var step = 0;
        //if ( Math.abs(e.pageX-lastX) > step && Math.abs(e.pageY-lastY) > step ) {
            dropTarget = findDropTarget(avatar);
            dropTarget && dropTarget.onDragMove(avatar, e);
            if (lastDropTarget && (!dropTarget || lastDropTarget.id != dropTarget.id)) {
                lastDropTarget.onDragLeave();

            }
            lastDropTarget = dropTarget;

            lastX = e.pageX;
            lastY = e.pageY;
        //}

        return false;
    }

    function onMouseUp(e) {
        if (e.which != 1 ) {
            return false;
        }

        if (avatar) {

            if (dropTarget) {
                dropTarget.onDragEnd(avatar, e);
                avatar.onDragEnd();
            } else {
                avatar.onDragCancel();
            }

        }

        cleanUp();
    }

    function cleanUp() {
        dragChip = avatar = dropTarget = null;
    }

    function findDragChip(event) {
        var elem = event.target;
        while(elem != document && !$(elem).hasClass('drag_chip')) {
            elem = elem.parentNode;
        }

        if (!$(elem).hasClass('drag_chip')) {
            return null;
        }

        return new DragChip(elem);
    }

    function findDropTarget(avatar) {
        var border_chips = $('.is_border_mark');

        for (var i = border_chips.length - 1; i >= 0; i--) {
            var target = new DropTarget(border_chips[i])
            if (target.concateWith(avatar))
                return target;
        }
        return null;
    }

    document.ondragstart = function() {
        return false;
    }

    document.onmousemove = onMouseMove;
    document.onmouseup = onMouseUp;
    document.onmousedown = onMouseDown;
};

function DragChip(elem) {
    elem.dragChipElem = this;
    this._elem = elem;

    this.makeAvatar = function () {
        return new DragAvatar(this, this._elem);
    };

    this.onDragStart = function (downX, downY, event) {
        var avatar = this.makeAvatar();
        if (!avatar.initFromEvent(downX, downY, event)) {
            return false;
        }
        return avatar;
    }
}

function DragAvatar(dragChip, dragElem) {
    this._dragChip = dragChip;
    this._dragChipElem = dragElem;
    this._elem = dragElem;
    this._currentTargetElem = null;

    this._destroy = function () {
        this._elem.parentNode.removeChild(this._elem);
    }

    this.initFromEvent = function (downX, downY, event) {
        //if (event.target.tagName != 'DIV') return false;

        //this._dragChipElem = event.target;
        var elem = this._elem = this._dragChipElem.cloneNode(true);
        elem.removeAttribute('id');
        elem.className = elem.className + ' avatar';

        var coords = $(this._dragChipElem).offset();
        this._shiftX = downX - coords.left;
        this._shiftY = downY - coords.top;

        document.body.appendChild(elem);
        elem.style.zIndex = 9999;
        elem.style.position = 'absolute';

        return true;
    }

    this.getDragInfo = function (event) {
        return {
            elem: this._elem,
            dragChipElem: this._dragChipElem,
            dragChip: this._dragChip
        }
    }

    this.onDragMove = function(event) {
        this._elem.style.left = event.pageX - this._shiftX + 'px';
        this._elem.style.top = event.pageY - this._shiftY + 'px';
    }

    this.onDragCancel = function () {
        this._destroy()
    }

    this.onDragEnd = function () {
        this._destroy()
    }

    this.getMetric = function () {
        return {
            x: parseInt(this._elem.style.left),
            y: parseInt(this._elem.style.top),
            width: this._elem.offsetWidth,
            height: this._elem.offsetHeight
        }
    }
}

function DropTarget(elem) {
    elem.dropTarget = this;
    this._elem = elem;
    this.id = elem.id;

    this._hideHoverIndication = function (avatar) {
    }

    this._showHoverIndication = function (avatar) {
    }

    this.onDragMove = function (avatar, event) {
        $(this._elem).css('border', '3px solid red');
    }

    this.onDragEnter = function(fromDropTarget, avatar, event) {
    }

    this.onDragLeave = function(toDropTarget, avatar, event) {
        $(this._elem).css('border', 'none');
    }

    this.onDragEnd = function (avatar, event) {
        console.log('Chip on Table', avatar.getDragInfo().dragChip);
    }

    this.getMetric = function () {
        var pos = $(elem).offset();
        return {
            x: pos.left,
            y: pos.top,
            width: this._elem.offsetWidth,
            height: this._elem.offsetHeight
        }
    }

    this.concateWith = function (avatar) {
        var d = 100;
        var a_metric = avatar.getMetric()
        var x1 = a_metric.x, x2 = x1 + a_metric.width, y1 = a_metric.y, y2 = y1 + a_metric.height;

        var t_metric = this.getMetric();
        var l = t_metric.x, r = l + t_metric.width, t = t_metric.y, b = t + t_metric.height;

        var ts = Math.abs(t - y1) <= d;
        var bs = Math.abs(b - y2) <= d;
        var ls = Math.abs(l - x1) <= d;
        var rs = Math.abs(r - x2) <= d;

        if (ts && bs && ls && rs)
            return true;

        return false;
    }
}
