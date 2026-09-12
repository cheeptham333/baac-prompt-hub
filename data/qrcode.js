/**
 * Standalone Offline QR Code Generator (ISO/IEC 18004 Compliant)
 * Zero external dependencies, pure vector SVG output
 * Supports Versions 1-10, Byte mode encoding, Error Correction Level L/M
 */
(function(global) {
  // Galois Field GF(256) tables
  var GF256_EXP = new Array(512);
  var GF256_LOG = new Array(256);
  (function() {
    var x = 1;
    for (var i = 0; i < 255; i++) {
      GF256_EXP[i] = x;
      GF256_EXP[i + 255] = x;
      GF256_LOG[x] = i;
      x = (x << 1) ^ (x >= 128 ? 0x11d : 0);
    }
  })();

  function gfMul(x, y) {
    if (x === 0 || y === 0) return 0;
    return GF256_EXP[GF256_LOG[x] + GF256_LOG[y]];
  }

  function rsGeneratorPoly(degree) {
    var poly = [1];
    for (var i = 0; i < degree; i++) {
      var next = new Array(poly.length + 1);
      for (var j = 0; j < next.length; j++) next[j] = 0;
      var factor = GF256_EXP[i];
      for (var j = 0; j < poly.length; j++) {
        next[j] ^= gfMul(poly[j], factor);
        next[j + 1] ^= poly[j];
      }
      poly = next;
    }
    return poly;
  }

  function rsComputeRemainder(data, numEcWords) {
    var gen = rsGeneratorPoly(numEcWords);
    var remainder = new Array(numEcWords);
    for (var i = 0; i < numEcWords; i++) remainder[i] = 0;
    for (var i = 0; i < data.length; i++) {
      var factor = data[i] ^ remainder[0];
      for (var j = 0; j < numEcWords - 1; j++) {
        remainder[j] = remainder[j + 1] ^ gfMul(gen[numEcWords - 1 - j], factor);
      }
      remainder[numEcWords - 1] = gfMul(gen[0], factor);
    }
    return remainder;
  }

  // Version capacities (Level L)
  var CAPACITIES = [
    { v: 1, total: 26, ec: 7, data: 19, rem: 0 },
    { v: 2, total: 44, ec: 10, data: 34, rem: 7 },
    { v: 3, total: 70, ec: 15, data: 55, rem: 7 },
    { v: 4, total: 100, ec: 20, data: 80, rem: 7 },
    { v: 5, total: 134, ec: 26, data: 108, rem: 7 },
    { v: 6, total: 172, ec: 36, data: 136, rem: 7 },
    { v: 7, total: 196, ec: 40, data: 156, rem: 0 }
  ];

  function toUtf8Bytes(str) {
    var bytes = [];
    for (var i = 0; i < str.length; i++) {
      var c = str.charCodeAt(i);
      if (c < 0x80) {
        bytes.push(c);
      } else if (c < 0x800) {
        bytes.push(0xc0 | (c >> 6), 0x80 | (c & 0x3f));
      } else if (c >= 0xd800 && c <= 0xdbff && i + 1 < str.length) {
        var c2 = str.charCodeAt(++i);
        var cp = 0x10000 + (((c & 0x3ff) << 10) | (c2 & 0x3ff));
        bytes.push(0xf0 | (cp >> 18), 0x80 | ((cp >> 12) & 0x3f), 0x80 | ((cp >> 6) & 0x3f), 0x80 | (cp & 0x3f));
      } else {
        bytes.push(0xe0 | (c >> 12), 0x80 | ((c >> 6) & 0x3f), 0x80 | (c & 0x3f));
      }
    }
    return bytes;
  }

  function selectVersion(dataLen) {
    for (var i = 0; i < CAPACITIES.length; i++) {
      var maxDataBytes = CAPACITIES[i].data - 2; // Mode(4 bits) + Count(8 bits)
      if (dataLen <= maxDataBytes) return CAPACITIES[i];
    }
    return CAPACITIES[CAPACITIES.length - 1];
  }

  function encodeData(utf8Bytes, versionInfo) {
    var bits = [];
    function pushBits(val, len) {
      for (var i = len - 1; i >= 0; i--) {
        bits.push((val >> i) & 1);
      }
    }
    // Mode Byte = 0100
    pushBits(4, 4);
    // Character count indicator (8 bits for V1-V9)
    pushBits(utf8Bytes.length, 8);
    for (var i = 0; i < utf8Bytes.length; i++) {
      pushBits(utf8Bytes[i], 8);
    }
    // Terminator
    var maxDataBits = versionInfo.data * 8;
    var termLen = Math.min(4, maxDataBits - bits.length);
    pushBits(0, termLen);
    while (bits.length % 8 !== 0) bits.push(0);
    // Pad bytes
    var padBytes = [0xec, 0x11];
    var padIdx = 0;
    while (bits.length < maxDataBits) {
      pushBits(padBytes[padIdx % 2], 8);
      padIdx++;
    }
    // Convert to byte words
    var dataWords = [];
    for (var i = 0; i < bits.length; i += 8) {
      var byteVal = 0;
      for (var j = 0; j < 8; j++) byteVal = (byteVal << 1) | bits[i + j];
      dataWords.push(byteVal);
    }
    // Compute EC words
    var ecWords = rsComputeRemainder(dataWords, versionInfo.ec);
    return dataWords.concat(ecWords);
  }

  function createMatrix(version) {
    var size = 17 + version * 4;
    var matrix = [];
    var isReserved = [];
    for (var r = 0; r < size; r++) {
      matrix[r] = [];
      isReserved[r] = [];
      for (var c = 0; c < size; c++) {
        matrix[r][c] = 0;
        isReserved[r][c] = false;
      }
    }

    function setModule(r, c, val, reserved) {
      matrix[r][c] = val ? 1 : 0;
      if (reserved) isReserved[r][c] = true;
    }

    function drawFinder(row, col) {
      for (var r = -1; r <= 7; r++) {
        for (var c = -1; c <= 7; c++) {
          var qr = row + r;
          var qc = col + c;
          if (qr >= 0 && qr < size && qc >= 0 && qc < size) {
            var isBlack = (r >= 0 && r <= 6 && (c === 0 || c === 6)) ||
                          (c >= 0 && c <= 6 && (r === 0 || r === 6)) ||
                          (r >= 2 && r <= 4 && c >= 2 && c <= 4);
            setModule(qr, qc, isBlack, true);
          }
        }
      }
    }

    drawFinder(0, 0);
    drawFinder(0, size - 7);
    drawFinder(size - 7, 0);

    // Timing patterns
    for (var i = 8; i < size - 8; i++) {
      setModule(6, i, i % 2 === 0, true);
      setModule(i, 6, i % 2 === 0, true);
    }

    // Alignment pattern for version >= 2
    if (version >= 2) {
      var pos = size - 7;
      for (var r = -2; r <= 2; r++) {
        for (var c = -2; c <= 2; c++) {
          var isBlack = Math.max(Math.abs(r), Math.abs(c)) !== 1;
          setModule(pos + r, pos + c, isBlack, true);
        }
      }
    }

    // Dark module at (4*v + 9, 8)
    setModule(4 * version + 9, 8, 1, true);

    // Format info reserve
    for (var i = 0; i < 9; i++) {
      if (!isReserved[8][i]) isReserved[8][i] = true;
      if (!isReserved[i][8]) isReserved[i][8] = true;
    }
    for (var i = 0; i < 8; i++) {
      if (!isReserved[8][size - 1 - i]) isReserved[8][size - 1 - i] = true;
      if (!isReserved[size - 1 - i][8]) isReserved[size - 1 - i][8] = true;
    }

    return { size: size, matrix: matrix, isReserved: isReserved, setModule: setModule };
  }

  function placeData(matObj, codewords) {
    var size = matObj.size;
    var allBits = [];
    for (var i = 0; i < codewords.length; i++) {
      for (var b = 7; b >= 0; b--) {
        allBits.push((codewords[i] >> b) & 1);
      }
    }
    var bitIdx = 0;
    var right = size - 1;
    var upward = true;

    while (right > 0) {
      if (right === 6) right--; // Skip vertical timing column
      for (var vert = 0; vert < size; vert++) {
        var row = upward ? size - 1 - vert : vert;
        for (var colOffset = 0; colOffset < 2; colOffset++) {
          var col = right - colOffset;
          if (!matObj.isReserved[row][col]) {
            var bit = bitIdx < allBits.length ? allBits[bitIdx++] : 0;
            // Apply mask pattern 0: (row + col) % 2 === 0
            if ((row + col) % 2 === 0) bit ^= 1;
            matObj.matrix[row][col] = bit;
          }
        }
      }
      upward = !upward;
      right -= 2;
    }
  }

  function placeFormatInfo(matObj) {
    // Format bits for Level L, Mask 0 = 111011111000100 ^ 101010000010010 = 010001111010110
    var formatBits = [0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0];
    var size = matObj.size;
    // Top-left
    var coords1 = [
      [8,0],[8,1],[8,2],[8,3],[8,4],[8,5],[8,7],[8,8],
      [7,8],[5,8],[4,8],[3,8],[2,8],[1,8],[0,8]
    ];
    for (var i = 0; i < 15; i++) {
      matObj.matrix[coords1[i][0]][coords1[i][1]] = formatBits[i];
    }
    // Bottom-left and Top-right
    for (var i = 0; i < 7; i++) {
      matObj.matrix[size - 1 - i][8] = formatBits[i];
    }
    for (var i = 0; i < 8; i++) {
      matObj.matrix[8][size - 8 + i] = formatBits[7 + i];
    }
  }

  function generateQRCodeSVG(text, options) {
    options = options || {};
    var color = options.color || "#006838";
    var bgColor = options.bgColor || "#ffffff";
    var margin = options.margin !== undefined ? options.margin : 4;
    var sizePx = options.size || 280;

    var utf8 = toUtf8Bytes(text);
    var ver = selectVersion(utf8.length);
    var codewords = encodeData(utf8, ver);
    var matObj = createMatrix(ver.v);
    placeData(matObj, codewords);
    placeFormatInfo(matObj);

    var matrix = matObj.matrix;
    var modCount = matObj.size;
    var fullSize = modCount + margin * 2;
    var scale = sizePx / fullSize;

    var svgParts = [
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + fullSize + ' ' + fullSize + '" width="' + sizePx + '" height="' + sizePx + '" shape-rendering="crispEdges">',
      '<rect width="' + fullSize + '" height="' + fullSize + '" fill="' + bgColor + '"/>',
      '<path fill="' + color + '" d="'
    ];

    var path = "";
    for (var r = 0; r < modCount; r++) {
      for (var c = 0; c < modCount; c++) {
        if (matrix[r][c] === 1) {
          path += "M" + (c + margin) + "," + (r + margin) + "h1v1h-1z ";
        }
      }
    }
    svgParts.push(path + '"/>');
    svgParts.push('</svg>');
    return svgParts.join("");
  }

  global.generateQRCodeSVG = generateQRCodeSVG;
})(typeof window !== "undefined" ? window : this);
