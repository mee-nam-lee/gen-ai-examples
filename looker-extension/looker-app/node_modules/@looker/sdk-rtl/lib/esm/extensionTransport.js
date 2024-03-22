"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ExtensionTransport = void 0;
function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); enumerableOnly && (symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; })), keys.push.apply(keys, symbols); } return keys; }
function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = null != arguments[i] ? arguments[i] : {}; i % 2 ? ownKeys(Object(source), !0).forEach(function (key) { _defineProperty(target, key, source[key]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } return target; }
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }
function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }
function _defineProperty(obj, key, value) { key = _toPropertyKey(key); if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }
function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return typeof key === "symbol" ? key : String(key); }
function _toPrimitive(input, hint) { if (typeof input !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (typeof res !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }
class ExtensionTransport {
  constructor(options, hostConnection) {
    this.options = options;
    this.hostConnection = hostConnection;
    _defineProperty(this, "observer", void 0);
    this.options = options;
    this.hostConnection = hostConnection;
  }
  rawRequest(method, path, queryParams, body, authenticator, options) {
    var _this = this;
    return _asyncToGenerator(function* () {
      var response = yield _this.hostConnection.rawRequest(method, path, body, queryParams, authenticator, options);
      return _this.observer ? _this.observer(response) : response;
    })();
  }
  request(method, path, queryParams, body, authenticator, options) {
    var _this2 = this;
    return _asyncToGenerator(function* () {
      return _this2.hostConnection.request(method, path, body, queryParams, authenticator, options);
    })();
  }
  stream(callback, method, path, queryParams, body, authenticator, options) {
    var _this3 = this;
    return _asyncToGenerator(function* () {
      options = options ? _objectSpread(_objectSpread({}, _this3.options), options) : _this3.options;
      return _this3.hostConnection.stream(callback, method, path, body, queryParams, authenticator, options);
    })();
  }
  parseResponse(_raw) {
    var result = {
      ok: false,
      error: new Error('Should not be called!')
    };
    return Promise.resolve(result);
  }
}
exports.ExtensionTransport = ExtensionTransport;
//# sourceMappingURL=extensionTransport.js.map