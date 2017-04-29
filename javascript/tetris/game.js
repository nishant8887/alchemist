T=[[0, 0, 1, 0],
   [0, 1, 1, 0],
   [0, 0, 1, 0],
   [0, 0, 0, 0]];

S=[[0, 0, 0, 0],
   [0, 1, 1, 0],
   [1, 1, 0, 0],
   [0, 0, 0, 0]];

O=[[0, 0, 0, 0],
   [0, 1, 1, 0],
   [0, 1, 1, 0],
   [0, 0, 0, 0]];

L=[[0, 1, 0, 0],
   [0, 1, 0, 0],
   [0, 1, 1, 0],
   [0, 0, 0, 0]];

J=[[0, 0, 1, 0],
   [0, 0, 1, 0],
   [0, 1, 1, 0],
   [0, 0, 0, 0]];

Z=[[0, 0, 0, 0],
   [0, 1, 1, 0],
   [0, 0, 1, 1],
   [0, 0, 0, 0]];

I=[[0, 0, 0, 0],
   [1, 1, 1, 1],
   [0, 0, 0, 0],
   [0, 0, 0, 0]];

function Tetramino (parent) {
    this.matrix = undefined;
    this.type = undefined;
    this.size = 4;
    this.parent = parent;
    this.colors = ["purple","green","yellow","orange","blue","red","cyan"];
}

Tetramino.prototype = {
    reset: function () {
        var newtype = Math.floor((Math.random()*7)+1)-1;
        this.init(0, 0, newtype);
    },
    init: function (x, y, type) {
        this.x = x;
        this.y = y;
        this.type = type;
        
        switch(type) {
            case 0:
                this.matrix = T;
                break;
            case 1:
                this.matrix = S;
                break;
            case 2:
                this.matrix = O;
                break;
            case 3:
                this.matrix = L;
                break;
            case 4:
                this.matrix = J;
                break;
            case 5:
                this.matrix = Z;
                break;
            case 6:
                this.matrix = I;
                break;
            default:
                this.matrix = T;
                this.type = 0;
        }
        this.render();
    },
    render: function () {
        var k = 1;
        for(var i=0; i < this.size; i++) {
            for(var j=0; j < this.size; j++) {
                if(this.matrix[i][j] == 1) {
                    $('#t'+k).css("left",(this.x+i)*this.parent.blocksize);
                    $('#t'+k).css("top",(this.y+j)*this.parent.blocksize);
                    $('#t'+k).css("background-color",this.colors[this.type]);
                    k++;
                }
            }
        }
    },
    freeze: function () {
        for(var i=0; i < this.size; i++) {
            for(var j=0; j < this.size; j++) {
                if(this.matrix[i][j] == 1) {
                    this.parent.grid[this.x+i][this.y+j] = 1;
                    this.parent.render(this.x+i,this.y+j,this.colors[this.type]);
                    if(this.y+j <= this.parent.limit) {
                        //console.log("Game Over!");
                        this.parent.stop();
                    }
                }
            }
        }
        this.parent.check();
        this.reset();
    },
    move: function (type) {
        oldx = this.x;
        oldy = this.y;
        
        switch(type) {
            case 0:
                this.x++;
                break;
            case 1:
                this.x--;
                break;
            case 2:
                this.y++;
                break;
            case 3:
                this.y--;
                break;
            default:
        }
        if(!this.canmove()) {
            this.x = oldx;
            this.y = oldy;
            if(type == 2) {
                this.freeze();
            }
        }
        this.render();
    },
    canmove: function () {
        for(var i=0; i < this.size; i++) {
            for(var j=0; j < this.size; j++) {
                if(this.matrix[i][j] == 1) {
                    if(this.x+i >= this.parent.width) {
                        return false;
                    }
                    if(this.y+j >= this.parent.height) {
                        return false;
                    }
                    if(this.x+i < 0) {
                        return false;
                    }
                    if(this.y+j < 0) {
                        return false;
                    }
                    if(this.parent.grid[this.x+i][this.y+j] == 1) {
                        return false;
                    }
                }
            }
        }
        return true;
    },
    rotate: function () {
        if(!this.canrotate()) return;
        oldmatrix = this.matrix;
        Y = [];
        for(var i = 0; i < this.size; i++) {
            Y[i] = new Array();
            for(var j = 0; j < this.size; j++) {
                Y[i][this.size-1-j] = this.matrix[j][i];
            }
        }
        this.matrix = Y;
        if(!this.canmove()) {
            this.matrix = oldmatrix;
        }
        this.render();
    },
    canrotate: function () {
        var k, l, distance;
        var rotateflag = true;
        for(var i = 0; i < this.size; i++) {
            for(var j = 0; j < this.size; j++) {
                if(this.matrix[i][j] == 1) {
                    if(i < this.size/2) {
                        l = j + 1;
                    } else {
                        l = j - 1;
                    }
                    if(j < this.size/2) {
                        k = i - 1;
                    } else {
                        k = i + 1;
                    }
                    try {
                        if((this.parent.grid[this.x+k][this.y+j] == 1)&&(i != 0)&&(i != (this.size-1))) {
                            rotateflag = false;
                        }
                        if((this.parent.grid[this.x+i][this.y+l] == 1)&&(j != 0)&&(j != (this.size-1))) {
                            rotateflag = false;
                        }
                    } catch(e) {}
                }
            }
        }
        return rotateflag;
    }
}

function Map(width, height) {
    this.peice = undefined;
    this.width = width;
    this.height = height;
    this.blocksize = 15;
    this.limit = 5;
    this.grid = new Array();
    for(var i=0; i < this.width; i++) {
        this.grid[i] = new Array();
    }
}

Map.prototype = {
    init: function () {
        this.peice = new Tetramino(this);
        this.peice.reset();
    
        that = this;
        gameplay = setInterval(function () {
            that.peice.move(2);
        },200);
        
        $(document).bind('keypress', function(event) {
            switch(event.keyCode) {
                case 13:
                    that.peice.rotate();
                    break;
                case 37:
                    that.peice.move(1);
                    break;
                case 38:
                    //that.peice.move(3);
                    break;
                case 39:
                    that.peice.move(0);
                    break;
                case 40:
                    that.peice.move(2);
                    break;
                default:
            }
        });
    },
    stop: function () {
        clearInterval(gameplay);
        $(document).unbind('keypress');
    },
    render: function (x,y,color) {
        dom = '<div class="block" style="left: '+x*this.blocksize+'px; top: '+y*this.blocksize+'px; background-color: '+color+';"></div>';
        $("#map").append(dom);
    },
    check: function () {
        var fullflag;
        for(var j=0; j < this.height; j++) {
            fullflag = true;
            for(var i=0; i < this.width; i++) {
                if(!this.grid[i][j]) {
                    fullflag = false;
                    break;
                }
            }
            if(fullflag) {
                //console.log("Full grid row detected: " + j);
                this.updategrid(j);
            }
        }
    },
    updategrid: function (row) {
        for(var j=row; j > 0; j--) {
            for(var i=0; i < this.width; i++) {
                this.grid[i][j] = this.grid[i][j-1];
            }
        }
        var blocks = $('.block');
        for(var block in blocks) {
            if(blocks[block].offsetTop == row * this.blocksize) {
                blocks[block].parentNode.removeChild(blocks[block]);
            }
            if(blocks[block].offsetTop < row * this.blocksize) {
                blocks[block].style.top = (blocks[block].offsetTop + this.blocksize) + 'px';
            }
        }
    }
}

function init() {
    playgrid = new Map(20,30);
    playgrid.init();
}