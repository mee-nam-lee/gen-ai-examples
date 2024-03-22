"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ErrorDocRx = exports.ErrorDocNotFound = exports.ErrorDoc = exports.ErrorCodesUrl = void 0;
var _transport = require("./transport");
var _templateObject;
function _wrapRegExp() { _wrapRegExp = function _wrapRegExp(re, groups) { return new BabelRegExp(re, void 0, groups); }; var _super = RegExp.prototype, _groups = new WeakMap(); function BabelRegExp(re, flags, groups) { var _this = new RegExp(re, flags); return _groups.set(_this, groups || _groups.get(re)), _setPrototypeOf(_this, BabelRegExp.prototype); } function buildGroups(result, re) { var g = _groups.get(re); return Object.keys(g).reduce(function (groups, name) { var i = g[name]; if ("number" == typeof i) groups[name] = result[i];else { for (var k = 0; void 0 === result[i[k]] && k + 1 < i.length;) k++; groups[name] = result[i[k]]; } return groups; }, Object.create(null)); } return _inherits(BabelRegExp, RegExp), BabelRegExp.prototype.exec = function (str) { var result = _super.exec.call(this, str); if (result) { result.groups = buildGroups(result, this); var indices = result.indices; indices && (indices.groups = buildGroups(indices, this)); } return result; }, BabelRegExp.prototype[Symbol.replace] = function (str, substitution) { if ("string" == typeof substitution) { var groups = _groups.get(this); return _super[Symbol.replace].call(this, str, substitution.replace(/\$<([^>]+)>/g, function (_, name) { var group = groups[name]; return "$" + (Array.isArray(group) ? group.join("$") : group); })); } if ("function" == typeof substitution) { var _this = this; return _super[Symbol.replace].call(this, str, function () { var args = arguments; return "object" != typeof args[args.length - 1] && (args = [].slice.call(args)).push(buildGroups(args, _this)), substitution.apply(this, args); }); } return _super[Symbol.replace].call(this, str, substitution); }, _wrapRegExp.apply(this, arguments); }
function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) _setPrototypeOf(subClass, superClass); }
function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }
function _defineProperty(obj, key, value) { key = _toPropertyKey(key); if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }
function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return typeof key === "symbol" ? key : String(key); }
function _toPrimitive(input, hint) { if (typeof input !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (typeof res !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }
function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }
function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }
var ErrorCodesUrl = 'https://static-a.cdn.looker.app/errorcodes/';
exports.ErrorCodesUrl = ErrorCodesUrl;
var ErrorDocNotFound = '### No documentation found for ';
exports.ErrorDocNotFound = ErrorDocNotFound;
var ErrorDocPatternExpression = String.raw(_templateObject || (_templateObject = _taggedTemplateLiteral(["(?<redirector>(https://docs.looker.com/r|https://cloud.google.com/looker/docs/r)?/err/)(?<apiVersion>.*)/(?<statusCode>d{3})(?<apiPath>.*)"], ["(?<redirector>(https:\\/\\/docs\\.looker\\.com\\/r|https:\\/\\/cloud\\.google\\.com\\/looker\\/docs\\/r)?\\/err\\/)(?<apiVersion>.*)\\/(?<statusCode>\\d{3})(?<apiPath>.*)"])));
var ErrorDocRx = RegExp(ErrorDocPatternExpression, 'i');
exports.ErrorDocRx = ErrorDocRx;
var sdkUrlGet = function () {
  var _ref = _asyncToGenerator(function* (sdk, url) {
    return yield (0, _transport.sdkOk)(sdk.authSession.transport.request('GET', url));
  });
  return function sdkUrlGet(_x, _x2) {
    return _ref.apply(this, arguments);
  };
}();
class ErrorDoc {
  constructor(sdk) {
    var getter = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : sdkUrlGet;
    var cdnUrl = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : ErrorCodesUrl;
    this.sdk = sdk;
    this.getter = getter;
    this.cdnUrl = cdnUrl;
    _defineProperty(this, "_index", undefined);
  }
  load() {
    var _this = this;
    return _asyncToGenerator(function* () {
      if (!_this._index) {
        try {
          var result = yield _this.getter(_this.sdk, _this.indexUrl);
          if (typeof result === 'string') {
            result = JSON.parse(result);
          }
          _this._index = result;
        } catch (e) {
          return Promise.resolve({});
        }
      }
      return _this._index;
    })();
  }
  get indexUrl() {
    return this.contentUrl('index.json');
  }
  get index() {
    if (!this._index) {
      this.load().catch(reason => console.error(reason));
    }
    return this._index;
  }
  specPath(path) {
    var result = path.replace(/:\w+/g, found => "{".concat(found.substr(1), "}"));
    return result;
  }
  errorKey(docUrl) {
    var bits = this.parse(docUrl);
    if (!bits.redirector) return '';
    return this.specPath("".concat(bits.statusCode).concat(bits.apiPath));
  }
  notFound(key) {
    return "".concat(ErrorDocNotFound).concat(key);
  }
  getContent(url) {
    var _this2 = this;
    return _asyncToGenerator(function* () {
      try {
        return yield _this2.getter(_this2.sdk, url);
      } catch (e) {
        return Promise.resolve(_this2.notFound(e.message));
      }
    })();
  }
  content(docUrl) {
    var _this3 = this;
    return _asyncToGenerator(function* () {
      var key = _this3.errorKey(docUrl);
      if (!key) {
        return Promise.resolve(_this3.notFound('bad error code link'));
      }
      yield _this3.load();
      var item = _this3.index ? _this3.index[key] : undefined;
      if (!item) {
        var code = key.split('/')[0];
        item = _this3.index ? _this3.index[code] : undefined;
        if (!item) {
          return Promise.resolve(_this3.notFound(key));
        }
      }
      var url = _this3.contentUrl(item.url);
      return yield _this3.getContent(url);
    })();
  }
  contentUrl(urlPath) {
    return "".concat(this.cdnUrl).concat(urlPath);
  }
  methodName(errorMdUrl) {
    var _match$groups;
    var ErrorMdRx = _wrapRegExp(/(\w+)_\d{3}\.md/i, {
      name: 1
    });
    var match = errorMdUrl.match(ErrorMdRx);
    return (match === null || match === void 0 ? void 0 : (_match$groups = match.groups) === null || _match$groups === void 0 ? void 0 : _match$groups.name) || '';
  }
  parse(docUrl) {
    var _match$groups2, _match$groups3, _match$groups4, _match$groups5;
    var match = docUrl.match(ErrorDocRx);
    return {
      redirector: (match === null || match === void 0 ? void 0 : (_match$groups2 = match.groups) === null || _match$groups2 === void 0 ? void 0 : _match$groups2.redirector) || '',
      apiVersion: (match === null || match === void 0 ? void 0 : (_match$groups3 = match.groups) === null || _match$groups3 === void 0 ? void 0 : _match$groups3.apiVersion) || '',
      statusCode: (match === null || match === void 0 ? void 0 : (_match$groups4 = match.groups) === null || _match$groups4 === void 0 ? void 0 : _match$groups4.statusCode) || '',
      apiPath: (match === null || match === void 0 ? void 0 : (_match$groups5 = match.groups) === null || _match$groups5 === void 0 ? void 0 : _match$groups5.apiPath) || ''
    };
  }
}
exports.ErrorDoc = ErrorDoc;
//# sourceMappingURL=errorDoc.js.map