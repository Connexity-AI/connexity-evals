import { parseAsString } from 'nuqs/server';

export const emptyParser = {};

export const newAgentParser = {
  name: parseAsString,
};
