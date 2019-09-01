/**
 * How to use:
 *    when you do not want to download `tfjs-node` (for example avoiding compilation error of node-gyp)
 *    but you want to save model for node
 *    then copy this file and do:
 *    ```
 *    const tf = require('@tensorflow/tfjs');
 *    require('./tfjs-node-fs');
 *    // use model.save('file://...')
 *    ```
 */

const tf = require('@tensorflow/tfjs');
const tfc = require('@tensorflow/tfjs-core');
const fs = require('fs');
const i_path = require('path');
const dirname = i_path.dirname;
const join = i_path.join;
const resolve = i_path.resolve;
const promisify = require('util').promisify;

/**
 * @license
 * Copyright 2018 Google Inc. All Rights Reserved.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * =============================================================================
 */

function toBuffer(ab) {
  const view = new Uint8Array(ab);
  return Buffer.from(view); // copies data
}

function toArrayBuffer(buf) {
  if (Array.isArray(buf)) {
    // An Array of Buffers.
    let totalLength = 0;
    for (const buffer of buf) {
      totalLength += buffer.length;
    }

    const ab = new ArrayBuffer(totalLength);
    const view = new Uint8Array(ab);
    let pos = 0;
    for (const buffer of buf) {
      pos += buffer.copy(view, pos);
    }
    return ab;
  } else {
    // A single Buffer. Return a copy of the underlying ArrayBuffer slice.
    return buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
  }
}

// TODO(cais): Use explicit tfc.io.ModelArtifactsInfo return type below once it
// is available.
/**
 * Populate ModelArtifactsInfo fields for a model with JSON topology.
 * @param modelArtifacts
 * @returns A ModelArtifactsInfo object.
 */
function getModelArtifactsInfoForJSON(modelArtifacts) {
  if (modelArtifacts.modelTopology instanceof ArrayBuffer) {
    throw new Error('Expected JSON model topology, received ArrayBuffer.');
  }
  return {
    dateSaved: new Date(),
    modelTopologyType: 'JSON',
    modelTopologyBytes: modelArtifacts.modelTopology == null ?
        0 :
        Buffer.byteLength(JSON.stringify(modelArtifacts.modelTopology), 'utf8'),
    weightSpecsBytes: modelArtifacts.weightSpecs == null ?
        0 :
        Buffer.byteLength(JSON.stringify(modelArtifacts.weightSpecs), 'utf8'),
    weightDataBytes: modelArtifacts.weightData == null ?
        0 :
        modelArtifacts.weightData.byteLength,
  };
}


const stat = promisify(fs.stat);
const writeFile = promisify(fs.writeFile);
const readFile = promisify(fs.readFile);
const mkdir = promisify(fs.mkdir);

function doesNotExistHandler(name) {
  return e => {
    switch (e.code) {
      case 'ENOENT':
        throw new Error(`${name} ${e.path} does not exist: loading failed`);
      default:
        throw e;
    }
  };
}

class NodeFileSystem /*implements tfc.io.IOHandler*/ {
  /**
   * Constructor of the NodeFileSystem IOHandler.
   * @param path A single path or an Array of paths.
   *   For saving: expects a single path pointing to an existing or nonexistent
   *     directory. If the directory does not exist, it will be
   *     created.
   *   For loading:
   *     - If the model has JSON topology (e.g., `tf.Model`), a single path
   *       pointing to the JSON file (usually named `model.json`) is expected.
   *       The JSON file is expected to contain `modelTopology` and/or
   *       `weightsManifest`. If `weightManifest` exists, the values of the
   *       weights will be loaded from relative paths (relative to the directory
   *       of `model.json`) as contained in `weightManifest`.
   *     - If the model has binary (protocol buffer GraphDef) topology,
   *       an Array of two paths is expected: the first path should point to the
   *       .pb file and the second path should point to the weight manifest
   *       JSON file.
   */
  constructor(path) {
    this.path = path;
    this.MODEL_JSON_FILENAME = NodeFileSystem.MODEL_JSON_FILENAME;
    this.WEIGHTS_BINARY_FILENAME = NodeFileSystem.WEIGHTS_BINARY_FILENAME;
    this.MODEL_BINARY_FILENAME = NodeFileSystem.MODEL_BINARY_FILENAME;
    if (Array.isArray(path)) {
      tfc.util.assert(
          path.length === 2,
          () => 'file paths must have a length of 2, ' +
              `(actual length is ${path.length}).`);
      this.path = path.map(p => resolve(p));
    } else {
      this.path = resolve(path);
    }
  }

  async save(modelArtifacts) {
    if (Array.isArray(this.path)) {
      throw new Error('Cannot perform saving to multiple paths.');
    }

    await this.createOrVerifyDirectory();

    if (modelArtifacts.modelTopology instanceof ArrayBuffer) {
      throw new Error(
          'NodeFileSystem.save() does not support saving model topology ' +
          'in binary format yet.');
      // TODO(cais, nkreeger): Implement this. See
      //   https://github.com/tensorflow/tfjs/issues/343
    } else {
      const weightsBinPath = join(this.path, this.WEIGHTS_BINARY_FILENAME);
      const weightsManifest = [{
        paths: [this.WEIGHTS_BINARY_FILENAME],
        weights: modelArtifacts.weightSpecs
      }];
      const modelJSON = {
        modelTopology: modelArtifacts.modelTopology,
        weightsManifest,
      };
      const modelJSONPath = join(this.path, this.MODEL_JSON_FILENAME);
      await writeFile(modelJSONPath, JSON.stringify(modelJSON), 'utf8');
      await writeFile(
          weightsBinPath, Buffer.from(modelArtifacts.weightData), 'binary');

      return {
        // TODO(cais): Use explicit tfc.io.ModelArtifactsInfo type below once it
        // is available.
        // tslint:disable-next-line:no-any
        modelArtifactsInfo: getModelArtifactsInfoForJSON(modelArtifacts)
      };
    }
  }
  async load() {
    return Array.isArray(this.path) ? this.loadBinaryModel() :
                                      this.loadJSONModel();
  }

  async loadBinaryModel() {
    const topologyPath = this.path[0];
    const weightManifestPath = this.path[1];
    const topology =
        await stat(topologyPath).catch(doesNotExistHandler('Topology Path'));
    const weightManifest =
        await stat(weightManifestPath)
            .catch(doesNotExistHandler('Weight Manifest Path'));

    // `this.path` can be either a directory or a file. If it is a file, assume
    // it is model.json file.
    if (!topology.isFile()) {
      throw new Error('File specified for topology is not a file!');
    }
    if (!weightManifest.isFile()) {
      throw new Error('File specified for the weight manifest is not a file!');
    }

    const modelTopology = await readFile(this.path[0]);
    const weightsManifest = JSON.parse(await readFile(this.path[1], 'utf8'));

    const modelArtifacts = {
      modelTopology,
    };
    const [weightSpecs, weightData] =
        await this.loadWeights(weightsManifest, this.path[1]);

    modelArtifacts.weightSpecs = weightSpecs;
    modelArtifacts.weightData = weightData;

    return modelArtifacts;
  }

  async loadJSONModel() {
    const path = this.path;
    const info = await stat(path).catch(doesNotExistHandler('Path'));

    // `path` can be either a directory or a file. If it is a file, assume
    // it is model.json file.
    if (info.isFile()) {
      const modelJSON = JSON.parse(await readFile(path, 'utf8'));

      const modelArtifacts = {
        modelTopology: modelJSON.modelTopology,
      };
      if (modelJSON.weightsManifest != null) {
        const [weightSpecs, weightData] =
            await this.loadWeights(modelJSON.weightsManifest, path);
        modelArtifacts.weightSpecs = weightSpecs;
        modelArtifacts.weightData = weightData;
      }
      return modelArtifacts;
    } else {
      throw new Error(
          'The path to load from must be a file. Loading from a directory ' +
          'is not supported.');
    }
  }

  async loadWeights(weightsManifest, path) {
    const dirName = dirname(path);
    const buffers = [];
    const weightSpecs = [];
    for (let i = 0, n = weightsManifest.length; i < n; i++) {
      const group = weightsManifest[i];
      for (let j = 0, m = group.paths.length; j < m; j++) {
        const path = group.paths[j];
        const weightFilePath = join(dirName, path);
        const buffer = await readFile(weightFilePath)
                           .catch(doesNotExistHandler('Weight file'));
        buffers.push(buffer);
      }
      weightSpecs.push(...group.weights);
    }
    return [weightSpecs, toArrayBuffer(buffers)];
  }

  /**
   * For each item in `this.path`, creates a directory at the path or verify
   * that the path exists as a directory.
   */
  async createOrVerifyDirectory() {
    const paths = Array.isArray(this.path) ? this.path : [this.path];
    for (let i = 0, n = paths.length; i < n; i++) {
      let path = paths[i];
      try {
        await mkdir(path);
      } catch (e) {
        if (e.code === 'EEXIST') {
          if ((await stat(path)).isFile()) {
            throw new Error(
                `Path ${path} exists as a file. The path must be ` +
                `nonexistent or point to a directory.`);
          }
          // else continue, the directory exists
        } else {
          throw e;
        }
      }
    }
  }
}
NodeFileSystem.URL_SCHEME = 'file://';
NodeFileSystem.MODEL_JSON_FILENAME = 'model.json';
NodeFileSystem.WEIGHTS_BINARY_FILENAME = 'weights.bin';
NodeFileSystem.MODEL_BINARY_FILENAME = 'tensorflowjs.pb';


const nodeFileSystemRouter = (url) => {
  if (Array.isArray(url)) {
    if (url.every(
            urlElement => urlElement.startsWith(NodeFileSystem.URL_SCHEME))) {
      return new NodeFileSystem(url.map(
          urlElement => urlElement.slice(NodeFileSystem.URL_SCHEME.length)));
    } else {
      return null;
    }
  } else {
    if (url.startsWith(NodeFileSystem.URL_SCHEME)) {
      return new NodeFileSystem(url.slice(NodeFileSystem.URL_SCHEME.length));
    } else {
      return null;
    }
  }
};
// Registration of `nodeFileSystemRouter` is done in index.ts.

/**
 * Factory function for Node.js native file system IO Handler.
 *
 * @param path A single path or an Array of paths.
 *   For saving: expects a single path pointing to an existing or nonexistent
 *     directory. If the directory does not exist, it will be
 *     created.
 *   For loading:
 *     - If the model has JSON topology (e.g., `tf.Model`), a single path
 *       pointing to the JSON file (usually named `model.json`) is expected.
 *       The JSON file is expected to contain `modelTopology` and/or
 *       `weightsManifest`. If `weightManifest` exists, the values of the
 *       weights will be loaded from relative paths (relative to the directory
 *       of `model.json`) as contained in `weightManifest`.
 *     - If the model has binary (protocol buffer GraphDef) topology,
 *       an Array of two paths is expected: the first path should point to the
 *        .pb file and the second path should point to the weight manifest
 *       JSON file.
 */
function fileSystem(path) {
  return new NodeFileSystem(path);
}

tf.io.registerLoadRouter(nodeFileSystemRouter);
tf.io.registerSaveRouter(nodeFileSystemRouter);


module.exports = {
   NodeFileSystem,
   fileSystem,
   nodeFileSystemRouter,
};
