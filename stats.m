function [] = stats(sigma_obs, sigma_prior, nsamples, fac, debug)

load map;

if (debug == 1)
    jac_map = jac_map(:,1:10);
    beta_map = beta_map(1:10);
end

[n, m] = size(jac_map);

fprintf('Calculating Hessian......')
H = speye(m)./sigma_prior^2 + jac_map'*jac_map./sigma_obs^2.*fac.*fac;
%H = inv(Cov_prior) + jac_map'*jac_map./sigma_obs^2.*fac.*fac;
fprintf('completed!\n')

fprintf('Calculating covariance......')
% Covariance
H = inv(H);
fprintf('completed!\n')

% Cholesky
fprintf('Calculating cholesky......')
eps_ = 1e-7;
H = chol(H + eps_.*speye(m))';
fprintf('completed!\n')

fprintf('Starting sampling......\n')
beta_samples = zeros(nsamples, m);
for i=1:nsamples
    s = randn(size(beta_map));
    beta_samples(i,:) = beta_map + H*s;
    fprintf('sample %i of %i\r', i, nsamples);
    % progress bar
    fileID = fopen(sprintf('beta_files/beta.opt.%i', i),'w');
    fprintf(fileID,'%12.13f\n',beta_samples(i,:));
    fclose(fileID);
end
fprintf('completed!\n')

diag_cov = diag(H);
diag_cov = reshape(diag_cov', nk, nj)';
diag_cov = sqrt(diag_cov);

beta_std = std(beta_samples);
beta_mean = mean(beta_samples);

save results beta_std beta_mean beta_map jac_map diag_cov
end


