const Joi = require('joi');

const detectionSchema = Joi.object({
  traffic: Joi.array().items(Joi.number()).min(1).required(),
  ip: Joi.string().ip().required()
});

module.exports = { detectionSchema };